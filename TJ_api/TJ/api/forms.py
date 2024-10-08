# api/forms.py

from django import forms
from .models import User, Department, Job, Goal, Attendance, Leave

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_path']

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'department']

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['description', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['time_in', 'time_out', 'status']
        widgets = {
            'time_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'time_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }