import base64
from datetime import datetime, timedelta, date
from calendar import monthrange
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .utils import is_ajax, classify_face
from .decorators import manager_required, employee_required
from django.http import JsonResponse
from django.contrib.messages import get_messages
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
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
from .filters import AttendanceFilter, LeaveFilter, GoalFilter, JobFilter, UserFilter

# hero view
def landing_view(req):
    return render(req, "landing.html")

# authentication views
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
                    return redirect("dashboard")
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


# face recognition attendance views
def mark_attendance_face(request):
    return render(request, 'mark_attendance_face.html')

@csrf_exempt
def find_user_view(request):
    if is_ajax(request):
        photo = request.POST.get('photo')
        if not photo:
            return JsonResponse({'success': False, 'error': 'No photo provided'})

        try:
            _, str_img = photo.split(';base64')
            decoded_file = base64.b64decode(str_img)
        except (ValueError, TypeError) as e:
            return JsonResponse({'success': False, 'error': 'Invalid photo format'})

        # Save the decoded image to the Log model
        log_entry = Log()
        log_entry.photo.save('upload.png', ContentFile(decoded_file))
        log_entry.save()

        # Classify the face using the saved photo
        res = classify_face(log_entry.photo.path)
        if res:
            user_exists = User.objects.filter(email=res).exists()
            if user_exists:
                user = User.objects.get(email=res)
                if user.profile_path and user.profile_path.name:
                    log_entry.profile = user
                    

                    # Authenticate the user using the custom backend
                    if user is not None:
                        if user.status == "REJECTED":
                            messages.error(request, "Your account was rejected.")
                        elif user.status == "PENDING":
                            messages.error(request, "Your account is not approved yet.")
                        else:
                            login(request, user)
                            log_entry.is_correct = True
                            log_entry.save()
                            # after logging in the user and saving the log entry, mark the attendance
                            mark_attendance(request)
                            return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})
                    else:
                        return JsonResponse({'success': False, 'error': 'Authentication failed'})
                else:
                    return JsonResponse({'success': False, 'error': 'User profile has no associated profile picture'})
        return JsonResponse({'success': False, 'error': 'User not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# dashboard view
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
    calendar_days = []
    current_day = first_day_of_month

    while current_day <= last_day_of_month:
        attendance = Attendance.objects.filter(user=request.user, date=current_day).first()
        calendar_days.append({
            'date': current_day,
            'attendance': attendance,
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

@login_required
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.status = "APPROVED"
    user.save()
    return redirect("dashboard")

@login_required
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


@manager_required
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

# leave views
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
            return redirect("leaves")
        
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
    if request.method == 'POST':
        leave.delete()
        messages.success(request, "Leave request deleted successfully.")
        return redirect('leaves')
    storage = get_messages(request)
    for _ in storage:
        pass
    return render(request, 'leave_confirm_delete.html', {'leave': leave})

@manager_required
@require_POST
def approve_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = 'APPROVED'
    leave.save()
    return redirect('leaves')

@manager_required
@require_POST
def reject_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = 'REJECTED'
    leave.save()
    return redirect('leaves')

# Goal views

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
def goals_detail(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == "POST":
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "Goal request updated successfully.")
            return redirect("goals")
    else:
        form = GoalForm(instance=goal)

    return render(request, 'goal_detail.html', {'form': form})



@login_required
def edit_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully.')
            return redirect('goals')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'goal_detail.html', {'form': form, 'goal_id': pk})

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
    calendar_days = []
    current_day = first_day_of_month

    while current_day <= last_day_of_month:
        attendance = Attendance.objects.filter(user=request.user, date=current_day).first()
        calendar_days.append({
            'date': current_day,
            'attendance': attendance,
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
    }
    return render(request, 'employee_attendance.html', context)

@login_required
def mark_attendance(request):
    today = date.today()
    attendance, created = Attendance.objects.get_or_create(
        user=request.user, date=today
    )

    if attendance.time_in and not attendance.time_out:
        attendance.time_out = datetime.now()
        attendance.status = 'PRESENT'
    elif not attendance.time_in:
        attendance.time_in = datetime.now()
        attendance.status = 'PRESENT'
    attendance.save()

    return redirect('employee_attendance')

@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted successfully.')
        return redirect('goals')
    return render(request, 'goal_confirm_delete.html', {'goal': goal})

# Department views
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



# Job views
@manager_required
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

# For admin users
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

# goal views
@login_required
def goals(request):
    goals = Goal.objects.filter(user=request.user).order_by('due_date')
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Goal added successfully.')
            return redirect('goals')
    else:
        form = GoalForm()
    
    # Separate goals into active and completed/expired
    active_goals = goals.filter(status__in=['ACTIVE', 'IN_PROGRESS'])
    completed_expired_goals = goals.exclude(completed=True).order_by('due_date')

    return render(request, 'goals.html', {
        'active_goals': active_goals,
        'completed_expired_goals': completed_expired_goals,
        'form': form
    })

@login_required
def add_goal(request):
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Goal added successfully.")
            return redirect("goals")
    else:
        form = GoalForm()
    return render(request, "goal_add.html", {"form": form})

