import base64
from datetime import datetime, timedelta, date
from calendar import monthrange
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.messages import get_messages
from .models import User, Department, Job, Goal, Attendance, Leave, Log
from .forms import (
    LoginForm,
    UserProfileForm,
    DepartmentForm,
    JobForm,
    GoalForm,
    LeaveForm,
    SignupForm,
)
from .decorators import manager_required, employee_required
from .filters import AttendanceFilter, LeaveFilter, GoalFilter, JobFilter, UserFilter
from .utils import is_ajax
from .face_recognition_utils import classify_face, classify_face_base64
import cloudinary.uploader

# Landing Page Views
def landing_view(req):
    return render(req, "landing.html")

# Authentication Views
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.status == "REJECTED":
                    messages.error(request, "Your account was rejected.")
                elif user.status == "PENDING":
                    messages.error(request, "Your account is not approved yet.")
                else:
                    login(request, user)
                    if user.role == "MANAGER" or user.role == "EMPLOYEE":
                        return redirect("dashboard")
                    elif user.role == "ADMIN":
                        return redirect(reverse('admin:index'))
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Your account has been created successfully!")
            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})

# Face Recognition Views
def mark_attendance_face(request):
    return render(request, 'mark_attendance_face.html')

@csrf_exempt
def find_user_view(request):
    if not is_ajax(request):
        return JsonResponse({'success': False, 'error': 'Invalid request'})

    photo = request.POST.get('photo')
    if not photo:
        return JsonResponse({'success': False, 'error': 'No photo provided'})

    try:
        # Extract the base64 encoded image
        _, str_img = photo.split(';base64,')

        # Classify the face directly from base64
        email = classify_face_base64(str_img)
        
        if not email:
            return JsonResponse({'success': False, 'error': 'Face not recognized'})

        try:
            user = User.objects.select_related('address').get(email=email, status='APPROVED')
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found or not approved'})

        if not user.profile_path:
            return JsonResponse({'success': False, 'error': 'No profile picture found'})

        # Upload to Cloudinary asynchronously
        upload_result = cloudinary.uploader.upload(
            f"data:image/jpeg;base64,{str_img}",
            folder="attendance_logs",
            quality=95,
            width=800,
            height=800,
            crop="limit"
        )
        
        # Create and save log entry
        log_entry = Log.objects.create(
            photo=upload_result['secure_url'],
            profile=user,
            is_correct=True
        )

        # Authenticate and mark attendance
        login(request, user)
        mark_attendance(request)
        return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Dashboard Views
@login_required
def dashboard(request):
    today = date.today()
    total_employees = User.objects.count()
    timed_in_today = Attendance.objects.filter(date=today, time_in__isnull=False).count()
    timed_out_today = Attendance.objects.filter(date=today, time_out__isnull=False).count()
    recent_attendance = Attendance.objects.order_by('-date', '-time_in')[:10]
    pending_users = User.objects.filter(status='PENDING')

    # Get the selected month from the request, default to the current month
    selected_month = request.GET.get('month', today.strftime('%Y-%m'))
    selected_month_date = datetime.strptime(selected_month, '%Y-%m')

    # Generate calendar data for the selected month
    year = selected_month_date.year
    month = selected_month_date.month
    first_day_of_month = date(year, month, 1)
    last_day_of_month = date(year, month, monthrange(year, month)[1])
    
    # Calculate padding days (Sunday = 0, Saturday = 6)
    padding_days = first_day_of_month.weekday()
    if padding_days == 6:  # If it's Sunday
        padding_days = 0
    else:
        padding_days += 1  # Shift by 1 to make Sunday first day
    
    calendar_days = []
    
    # Add padding days
    for _ in range(padding_days):
        calendar_days.append({
            'date': None,
            'attendance': None,
            'is_padding': True
        })
    
    # Add actual days
    current_day = first_day_of_month
    while current_day <= last_day_of_month:
        attendance = Attendance.objects.filter(user=request.user, date=current_day).first()
        weekday = current_day.weekday()
        is_weekend = weekday == 5 or weekday == 6  # Saturday = 5, Sunday = 6
        is_today = current_day == today
        
        calendar_days.append({
            'date': current_day,
            'attendance': attendance,
            'is_weekend': is_weekend,
            'is_today': is_today,
            'is_padding': False
        })
        current_day += timedelta(days=1)

    # Leave data for non-manager users
    if request.user.role != "MANAGER":
        total_leaves = Leave.objects.filter(user=request.user).count()
        used_leaves = Leave.objects.filter(user=request.user, status='APPROVED').count()
        remaining_leaves = total_leaves - used_leaves
    else:
        total_leaves = used_leaves = remaining_leaves = None

    context = {
        'total_employees': total_employees,
        'timed_in_today': timed_in_today,
        'timed_out_today': timed_out_today,
        'recent_attendance': recent_attendance,
        'pending_users': pending_users,
        'calendar_days': calendar_days,
        'total_leaves': total_leaves,
        'used_leaves': used_leaves,
        'remaining_leaves': remaining_leaves,
        'selected_month': selected_month_date,
    }
    return render(request, 'dashboard.html', context)

# User Management Views
@manager_required
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.status = "APPROVED"
    user.save()
    return redirect("dashboard")

@manager_required
def reject_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.status = "REJECTED"
    user.save()
    return redirect("dashboard")


@login_required
def profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            # Update session to prevent logout on password change
            update_session_auth_hash(request, user)
            messages.success(request, "Your profile was successfully updated.")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=request.user)

    storage = get_messages(request)
    for _ in storage:
        pass
    return render(request, "profile.html", {"form": form})

# Attendance Management Views
@login_required
def attendance(request):
    attendance_list = Attendance.objects.all().order_by("-time_in")
    attendance_filter = AttendanceFilter(request.GET, queryset=attendance_list)

    paginator = Paginator(attendance_filter.qs, 10)  # Show 10 records per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "filter": attendance_filter,
        "page_obj": page_obj,
    } 
    return render(request, "attendance.html", context)

@employee_required
@login_required
def employee_attendance(request):
    today = date.today()
    year = request.GET.get('year', today.year)
    month = request.GET.get('month', today.month)
    year, month = int(year), int(month)

    # Generate calendar data
    first_day_of_month = date(year, month, 1)
    last_day_of_month = date(year, month, monthrange(year, month)[1])
    
    # Calculate padding days (Sunday = 0, Saturday = 6)
    padding_days = first_day_of_month.weekday()
    if padding_days == 6:  # If it's Sunday
        padding_days = 0
    else:
        padding_days += 1  # Shift by 1 to make Sunday first day
    
    calendar_days = []
    
    # Add padding days
    for _ in range(padding_days):
        calendar_days.append({
            'date': None,
            'attendance': None,
            'is_padding': True
        })
    
    # Add actual days
    current_day = first_day_of_month
    while current_day <= last_day_of_month:
        attendance = Attendance.objects.filter(user=request.user, date=current_day).first()
        weekday = current_day.weekday()
        is_weekend = weekday == 5 or weekday == 6  # Saturday = 5, Sunday = 6
        is_today = current_day == today
        
        calendar_days.append({
            'date': current_day,
            'attendance': attendance,
            'is_weekend': is_weekend,
            'is_today': is_today,
            'is_padding': False
        })
        current_day += timedelta(days=1)

    today_attendance = Attendance.objects.filter(user=request.user, date=today).first()
    timed_in = today_attendance is not None and today_attendance.time_in is not None

    context = {
        'timed_in': timed_in,
        'calendar_days': calendar_days,
        'year': year,
        'month': month,
        'today': today,
        'selected_month': first_day_of_month,  
    }
    return render(request, 'employee_attendance.html', context)

@login_required
def mark_attendance(request):
    today = date.today()
    current_time = datetime.now()
    
    # Define shift times
    shift_start = current_time.replace(hour=9, minute=0, second=0, microsecond=0)  # 9:00 AM
    shift_end = current_time.replace(hour=17, minute=0, second=0, microsecond=0)   # 5:00 PM
    grace_period = timedelta(minutes=15)  # 15 minutes grace period
    
    attendance, created = Attendance.objects.get_or_create(
        user=request.user, date=today
    )

    if attendance.time_in and not attendance.time_out:
        # Time out
        attendance.time_out = current_time
        
        # Check if leaving early
        if current_time < shift_end:
            attendance.status = 'HALF_DAY'
            messages.warning(request, f'Early departure recorded at {current_time.strftime("%I:%M %p")}')
        else:
            attendance.status = 'PRESENT'
            messages.success(request, f'Time out recorded at {current_time.strftime("%I:%M %p")}')
            
    elif not attendance.time_in:
        # Time in
        attendance.time_in = current_time
        
        # Check if late
        if current_time > (shift_start + grace_period):
            attendance.status = 'LATE'
            messages.warning(request, f'Late arrival recorded at {current_time.strftime("%I:%M %p")}')
        else:
            attendance.status = 'PRESENT'
            messages.success(request, f'Time in recorded at {current_time.strftime("%I:%M %p")}')
    else:
        messages.warning(request, 'You have already completed your attendance for today.')
    
    attendance.save()
    return redirect('employee_attendance')

# Leave Management Views
@login_required
def leave_list(request):
    leaves_own = Leave.objects.filter(user=request.user).order_by("-status")
    leaves_all = Leave.objects.all().order_by("-status")
    leave_filter = ""
    if(request.user.role == "MANAGER"):
        leave_filter = LeaveFilter(request.GET, queryset=leaves_all)
    else:
        leave_filter = LeaveFilter(request.GET, queryset=leaves_own)
    filtered_leaves = leave_filter.qs
    paginator = Paginator(filtered_leaves, 10)  # Show 10 leaves per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Create a form instance for each leave request
    edit_leave_forms = {leave.id: LeaveForm(instance=leave) for leave in leaves_own}

    context = {
        'page_obj': page_obj,
        'edit_leave_forms': edit_leave_forms,
        'add_leave_form': LeaveForm(),
        'filter': leave_filter,
    }
    return render(request, 'leaves.html', context)

@login_required
def edit_leave(request, pk):
    leave = get_object_or_404(Leave, pk=pk, user=request.user)
    if leave.status != "PENDING":
        messages.error(request, "You cannot edit a leave request that is not pending.")
        return redirect("leaves")

    if request.method == "POST":
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            messages.success(request, "Leave request updated successfully.")
            return redirect("leaves")
    else:
        form = LeaveForm(instance=leave)

    return render(request, 'leave_detail.html', {'form': form})

@login_required
def request_leave(request):
    if request.method == "POST":
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user  # Set the current user as the leave requester
            leave.save()
            messages.success(request, "Leave request submitted successfully.")
            return redirect("leaves")
        else:
            messages.error(request, "Please check your form inputs and try again.")
        
    storage = get_messages(request)
    for _ in storage:
        pass
    return redirect("leaves")

@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(
        Leave, pk=pk, user=request.user
    )  # Ensure the leave belongs to the current user
    if leave.status != "PENDING":
        messages.error(request, "You cannot edit a leave request that is not pending.")
        return redirect("leaves")

    if request.method == "POST":
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            messages.success(request, "Leave request updated successfully.")
            return redirect("leaves")
    else:
        form = LeaveForm(instance=leave)

    storage = get_messages(request)
    for _ in storage:
        pass
    return render(request, 'leave_detail.html', {'form': form})

@login_required
def delete_leave(request, pk):
    leave = get_object_or_404(Leave, pk=pk, user=request.user)
    if leave.status != "PENDING":
        messages.error(request, "You cannot delete a leave request that is not pending.")
        return redirect("leaves")
    
    leave.delete()
    messages.success(request, "Leave request deleted successfully.")
    return redirect("leaves")

@manager_required
@require_POST
def approve_leave(request, leave_id):
    if request.user.role != "MANAGER":
        messages.error(request, "You don't have permission to approve leave requests.")
        return redirect("leaves")
    
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = "APPROVED"
    leave.save()
    messages.success(request, f"Leave request for {leave.user.get_full_name()} has been approved.")
    return redirect("leaves")

@manager_required
@require_POST
def reject_leave(request, leave_id):
    if request.user.role != "MANAGER":
        messages.error(request, "You don't have permission to reject leave requests.")
        return redirect("leaves")
    
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = "REJECTED"
    leave.save()
    messages.error(request, f"Leave request for {leave.user.get_full_name()} has been rejected.")
    return redirect("leaves")

# Goal Management Views
@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user).order_by("-due_date")
    goal_filter = GoalFilter(request.GET, queryset=goals)

    paginator = Paginator(goal_filter.qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Create a form instance for each goal
    edit_goal_forms = {goal.id: GoalForm(instance=goal) for goal in goals}

    context = {
        "page_obj": page_obj,
        "edit_goal_forms": edit_goal_forms,
        "add_goal_form": GoalForm(),
        "filter": goal_filter,
    }
    return render(request, "goals.html", context)

@login_required
def edit_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully.')
        else:
            messages.error(request, 'Please check your input and try again.')
        return redirect('goals')

@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted successfully.')
    return redirect('goals')

@login_required
def add_goal(request):
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Goal added successfully.")
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
    return redirect("goals")

@login_required
def toggle_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.completed = not goal.completed
    goal.save()
    status = "completed" if goal.completed else "uncompleted"
    messages.success(request, f"Goal marked as {status}.")
    return redirect("goals")

# Department Management Views
@manager_required
@require_POST
def add_department(request):
    form = DepartmentForm(request.POST)
    if form.is_valid():
        form.save()
    return redirect("jobs")

@manager_required
@require_POST
def delete_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    department.delete()
    return redirect('jobs')

# Job Management Views
@login_required
def jobs(request):
    departments = Department.objects.all()
    selected_department = request.GET.get("department")
    if selected_department:
        job_list = Job.objects.filter(department_id=selected_department).order_by("title")
    else:
        job_list = Job.objects.all().order_by("department", "title")

    job_filter = JobFilter(request.GET, queryset=job_list)
    paginator = Paginator(job_filter.qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "departments": departments,
        "selected_department": selected_department,
        "filter": job_filter,
        "page_obj": page_obj,
        "job_form": JobForm(),
        "department_form": DepartmentForm(),
    }
    return render(request, "jobs.html", context)

@manager_required
@require_POST
def add_job(request):
    form = JobForm(request.POST)
    if form.is_valid():
        job = form.save(commit=False)
        department_id = request.POST.get('department_id')
        if department_id:
            job.department = get_object_or_404(Department, id=department_id)
        job.save()
    return redirect("jobs")

@manager_required
@require_POST
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.delete()
    return redirect('jobs')

# Admin Management Views
@login_required
def user_list(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to view this page.")
        return redirect("dashboard")

    user_list = User.objects.all().order_by("first_name", "last_name")
    user_filter = UserFilter(request.GET, queryset=user_list)

    paginator = Paginator(user_filter.qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "filter": user_filter,
        "page_obj": page_obj,
    }
    return render(request, "user_list.html", context)
