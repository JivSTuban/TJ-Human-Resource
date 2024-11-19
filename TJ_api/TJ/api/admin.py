# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address, Department, Job, Goal, Attendance, Leave, Log


# User Management Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "status",
        "date_of_hire",
    )
    list_filter = ("role", "status", "date_of_hire")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone_number", "address")},
        ),
        ("Work info", {"fields": ("role", "date_of_hire", "status", "profile_path")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "date_of_hire",
                ),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


# Address Management Admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("street", "city", "country", "zip_code")
    search_fields = ("street", "city", "country")


# Department Management Admin
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)


# Job Management Admin
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "department")
    list_filter = ("department",)


# Goal Management Admin
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("user", "description", "completed", "due_date", "created_at")
    list_filter = ("due_date", "created_at")


# Attendance Management Admin
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "time_in", "time_out", "status")
    list_filter = ("status", "date")


# Leave Management Admin
@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ("user", "leave_type", "start_date", "end_date", "status")
    list_filter = ("leave_type", "status", "start_date")


# Face Recognition Log Admin
@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'photo', 'is_correct', 'created')
    list_filter = ('is_correct', 'created')
    search_fields = ('profile__email', 'profile__first_name', 'profile__last_name')
