# api/filters.py

import django_filters
from .models import User, Department, Job, Goal, Attendance, Leave


class AttendanceFilter(django_filters.FilterSet):
    date_range = django_filters.DateFromToRangeFilter(
        field_name="date",
        widget=django_filters.widgets.RangeWidget(attrs={"type": "date"}),
    )
    status = django_filters.ChoiceFilter(choices=Attendance.STATUS_CHOICES)

    class Meta:
        model = Attendance
        fields = ["date_range", "status"]


class LeaveFilter(django_filters.FilterSet):
    date_range = django_filters.DateFromToRangeFilter(
        field_name="start_date",
        widget=django_filters.widgets.RangeWidget(attrs={"type": "date"}),
    )
    leave_type = django_filters.ChoiceFilter(choices=Leave.LEAVE_TYPES)
    status = django_filters.ChoiceFilter(choices=Leave.STATUS_CHOICES)

    class Meta:
        model = Leave
        fields = ["date_range", "leave_type", "status"]


class GoalFilter(django_filters.FilterSet):
    due_date_range = django_filters.DateFromToRangeFilter(
        field_name="due_date",
        widget=django_filters.widgets.RangeWidget(attrs={"type": "date"}),
    )

    class Meta:
        model = Goal
        fields = ["due_date_range"]


class JobFilter(django_filters.FilterSet):
    department = django_filters.ModelChoiceFilter(
        queryset=Department.objects.all(), empty_label="All Departments"
    )
    title = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Job
        fields = ["department", "title"]


class UserFilter(django_filters.FilterSet):
    department = django_filters.ModelChoiceFilter(
        queryset=Department.objects.all(),
        empty_label="All Departments",
        field_name="job__department",
        distinct=True,
    )
    role = django_filters.ChoiceFilter(choices=User.ROLE_CHOICES)
    status = django_filters.ChoiceFilter(choices=User.STATUS_CHOICES)

    class Meta:
        model = User
        fields = ["department", "role", "status"]
