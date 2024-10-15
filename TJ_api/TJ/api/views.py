from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .decorators import manager_required
from django.contrib.messages import get_messages
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from .models import User, Department, Job, Goal, Attendance, Leave
from .forms import (
    LoginForm,
    UserProfileForm,
    DepartmentForm,
    JobForm,
    GoalForm,
    AttendanceForm,
    LeaveForm,
    SignupForm,
)
from .filters import AttendanceFilter, LeaveFilter, GoalFilter, JobFilter, UserFilter


def landing_view(req):
    return render(req, "landing.html")


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()

    storage = get_messages(request)
    for _ in storage:
        pass
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

    storage = get_messages(request)
    for _ in storage:
        pass

    return render(request, "signup.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user
    recent_goals = Goal.objects.filter(user=user).order_by("-created_at")[:5]
    recent_attendance = Attendance.objects.filter(user=user).order_by("-date")[:5]
    pending_leaves = Leave.objects.filter(user=user, status="PENDING")

    context = {
        "user": user,
        "recent_goals": recent_goals,
        "recent_attendance": recent_attendance,
        "pending_leaves": pending_leaves,
    }
    return render(request, "dashboard.html", context)


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


# Department views
@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, "department_list.html", {"departments": departments})


@login_required
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("department_list")
    else:
        form = DepartmentForm()
    return render(request, "department_form.html", {"form": form})


@login_required
def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect("department_list")
    else:
        form = DepartmentForm(instance=department)
    return render(request, "department_form.html", {"form": form})

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


@login_required
def mark_attendance(request):
    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(
        user=request.user, date=today, defaults={"status": "PRESENT"}
    )

    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance marked successfully.")
            return redirect("attendance_list")
    else:
        form = AttendanceForm(instance=attendance)

    storage = get_messages(request)
    for _ in storage:
        pass

    return render(request, "attendance.html", {"form": form})

# leave views
@login_required
def leave_list(request):
    leaves = Leave.objects.filter(user=request.user).order_by("-status")
    leave_filter = LeaveFilter(request.GET, queryset=leaves)
    filtered_leaves = leave_filter.qs

    paginator = Paginator(filtered_leaves, 10)  # Show 10 leaves per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Create a form instance for each leave request
    edit_leave_forms = {leave.id: LeaveForm(instance=leave) for leave in leaves}

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

@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted successfully.')
        return redirect('goals')
    return render(request, 'goal_confirm_delete.html', {'goal': goal})


@login_required
def job_list(request):
    job_list = Job.objects.all().order_by("department", "title")
    job_filter = JobFilter(request.GET, queryset=job_list)

    paginator = Paginator(job_filter.qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "filter": job_filter,
        "page_obj": page_obj,
    }
    return render(request, "job_list.html", context)


@login_required
def add_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("job_list")
    else:
        form = JobForm()

    return render(request, "job_form.html", {"form": form})


@login_required
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect("job_list")  # Redirect back to the job list after editing
    else:
        form = JobForm(instance=job)

    return render(request, "job_form.html", {"form": form, "job": job})


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
    return render(request, 'goals.html', {'form': form, 'goal_id': pk})

@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted successfully.')
        return redirect('goals')
    return render(request, 'delete_goal.html', {'goal': goal})
