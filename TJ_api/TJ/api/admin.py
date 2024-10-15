# Register your models here.
# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address, Department, Job, Goal, Attendance, Leave


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


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("street", "city", "country", "zip_code")
    search_fields = ("street", "city", "country")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "department")
    list_filter = ("department",)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("user", "description", "completed", "due_date", "created_at")
    list_filter = ("due_date", "created_at")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "time_in", "time_out", "status")
    list_filter = ("status", "date")


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ("user", "leave_type", "start_date", "end_date", "status")
    list_filter = ("leave_type", "status", "start_date")
