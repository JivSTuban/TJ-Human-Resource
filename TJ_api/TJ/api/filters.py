# api/filters.py

import django_filters
from django.forms.widgets import DateInput
from .models import User, Department, Job, Goal, Attendance, Leave


class AttendanceFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(field_name='user__first_name', lookup_expr='icontains', label='First Name')
    last_name = django_filters.CharFilter(field_name='user__last_name', lookup_expr='icontains', label='Last Name')
    date = django_filters.DateFilter(field_name='date', lookup_expr='exact', label='Date', widget=DateInput(attrs={"type": "date"}))

    class Meta:
        model = Attendance
        fields = ['first_name', 'last_name', 'date']


class LeaveFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name="start_date",
        widget=DateInput(attrs={"type": "date"}),
    )
    end_date = django_filters.DateFilter(
        field_name="end_date",
        widget=DateInput(attrs={"type": "date"}),
    )
    leave_type = django_filters.ChoiceFilter(choices=Leave.LEAVE_TYPES)
    status = django_filters.ChoiceFilter(choices=Leave.STATUS_CHOICES)

    class Meta:
        model = Leave
        fields = ["start_date", "end_date", "leave_type", "status"]


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
