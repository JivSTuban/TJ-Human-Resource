from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
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


def landing_view(request):
    return render(request, "api/landing.html")


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
    return render(request, "api/login.html", {"form": form})


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
    
    return render(request, "api/signup.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user
    recent_goals = Goal.objects.filter(user=user).order_by("-created_at")[:5]
    recent_attendance = Attendance.objects.filter(user=user).order_by("-date")[:5]
    pending_leaves = Leave.objects.filter(user=user, status="PENDING")

    context = {
        "recent_goals": recent_goals,
        "recent_attendance": recent_attendance,
        "pending_leaves": pending_leaves,
    }
    return render(request, "api/dashboard.html", context)


@login_required
def profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, "api/profile.html", {"form": form, "user": request.user})


# Department views
@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, "api/department_list.html", {"departments": departments})


@login_required
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("department_list")
    else:
        form = DepartmentForm()
    return render(request, "api/department_form.html", {"form": form})


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
    return render(request, "api/department_form.html", {"form": form})


@login_required
def attendance_list(request):
    attendance_list = Attendance.objects.filter(user=request.user).order_by("-date")
    attendance_filter = AttendanceFilter(request.GET, queryset=attendance_list)

    paginator = Paginator(attendance_filter.qs, 10)  # Show 10 records per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "filter": attendance_filter,
        "page_obj": page_obj,
    }
    return render(request, "api/attendance_list.html", context)


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

    return render(request, "api/attendance.html", {"form": form})


@login_required
def leave_list(request):
    leave_list = Leave.objects.filter(user=request.user).order_by("-start_date")
    leave_filter = LeaveFilter(request.GET, queryset=leave_list)

    paginator = Paginator(leave_filter.qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "filter": leave_filter,
        "page_obj": page_obj,
    }
    return render(request, "api/leave_list.html", context)


@login_required
def goal_list(request):
    goal_list = Goal.objects.filter(user=request.user).order_by("-due_date")
    goal_filter = GoalFilter(request.GET, queryset=goal_list)

    paginator = Paginator(goal_filter.qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "filter": goal_filter,
        "page_obj": page_obj,
    }
    return render(request, "api/goals.html", context)


# Create Goal
@login_required
def add_goal(request):
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user  # Set the current user as the goal owner
            goal.save()
            messages.success(request, "Goal created successfully.")
            return redirect("goal_list")
    else:
        form = GoalForm()
    return render(request, "api/goal_form.html", {"form": form})


# Edit Goal
@login_required
def edit_goal(request, pk):
    goal = get_object_or_404(
        Goal, pk=pk, user=request.user
    )  # Ensure the goal belongs to the current user
    if request.method == "POST":
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "Goal updated successfully.")
            return redirect("goal_list")
    else:
        form = GoalForm(instance=goal)
    return render(request, "api/goal_form.html", {"form": form})


# Delete Goal
@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == "POST":
        goal.delete()
        messages.success(request, "Goal deleted successfully.")
        return redirect("goal_list")
    return render(request, "api/confirm_delete.html", {"object": goal, "type": "goal"})


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
    return render(request, "api/job_list.html", context)


@login_required
def add_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("job_list")
    else:
        form = JobForm()

    return render(request, "api/job_form.html", {"form": form})


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

    return render(request, "api/job_form.html", {"form": form, "job": job})


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
    return render(request, "api/user_list.html", context)


# Create Leave
@login_required
def request_leave(request):
    if request.method == "POST":
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user  # Set the current user as the leave requester
            leave.save()
            messages.success(request, "Leave request submitted successfully.")
            return redirect("leave_list")
    else:
        form = LeaveForm()
    return render(request, "api/leave_form.html", {"form": form})


# Edit Leave
@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(
        Leave, pk=pk, user=request.user
    )  # Ensure the leave belongs to the current user
    if leave.status != "PENDING":
        messages.error(request, "You cannot edit a leave request that is not pending.")
        return redirect("leave_list")

    if request.method == "POST":
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            messages.success(request, "Leave request updated successfully.")
            return redirect("leave_list")
    else:
        form = LeaveForm(instance=leave)
    return render(request, "api/leave_form.html", {"form": form})


# Delete Leave
@login_required
def delete_leave(request, pk):
    leave = get_object_or_404(Leave, pk=pk, user=request.user)
    if leave.status != "PENDING":
        messages.error(
            request, "You cannot delete a leave request that is not pending."
        )
        return redirect("leave_list")

    if request.method == "POST":
        leave.delete()
        messages.success(request, "Leave request deleted successfully.")
        return redirect("leave_list")
    return render(
        request, "api/confirm_delete.html", {"object": leave, "type": "leave"}
    )
