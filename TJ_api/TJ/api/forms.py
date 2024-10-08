from django import forms
from .models import User, Department, Job, Goal, Attendance, Leave, Address
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class UserProfileForm(forms.ModelForm):
    street = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Street")
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), label="City")
    country = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Country")
    zip_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Zip Code")

    class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'date_of_hire', 
            'profile_path',
            'job',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_hire': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_path': forms.FileInput(attrs={'class': 'form-control'}),
            'job': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'phone_number': 'Phone Number',
            'date_of_hire': 'Date of Hire',
            'profile_path': 'Profile Picture',
            'job': 'Job',
        }

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'password1', 
            'password2', 
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

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
        fields = ['leave_type', 'start_date', 'end_date', 'status']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }