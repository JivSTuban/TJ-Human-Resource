from django import forms
from django.contrib.auth import get_user_model
from .models import Department, Job, Goal, Attendance, Leave, Address
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from datetime import date
from django.utils import timezone

User = get_user_model()


# Authentication Forms
class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Password",
        required=True
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirm Password",
        required=True
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "password": "Password",
        }

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        # Make all fields required
        for field_name in self.fields:
            self.fields[field_name].required = True
            if 'class' not in self.fields[field_name].widget.attrs:
                self.fields[field_name].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Passwords do not match")

        return cleaned_data


# User Profile Forms
class UserProfileForm(forms.ModelForm):
    street = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Street",
        required=False,
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="City",
        required=False,
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Country",
        required=False,
    )
    zip_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Zip Code",
        required=False,
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "id": "new_password"}
        ),
        label="New Password",
        required=False,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "id": "confirm_password"}
        ),
        label="Confirm New Password",
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_hire",
            "profile_path",
            "job",
            'new_password',
            'confirm_password',
        ]
        widgets = {
            "date_of_hire": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.attrs = {"enctype": "multipart/form-data"}
        self.helper.add_input(Submit("submit", "Update Profile"))

        # Initialize address fields if user has an address
        if self.instance and self.instance.address:
            self.fields["street"].initial = self.instance.address.street
            self.fields["city"].initial = self.instance.address.city
            self.fields["country"].initial = self.instance.address.country
            self.fields["zip_code"].initial = self.instance.address.zip_code

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and new_password != confirm_password:
            raise forms.ValidationError("The new passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        # Handle address
        address_data = {
            "street": self.cleaned_data["street"],
            "city": self.cleaned_data["city"],
            "country": self.cleaned_data["country"],
            "zip_code": self.cleaned_data["zip_code"],
        }

        if user.address:
            # Update existing address
            for key, value in address_data.items():
                setattr(user.address, key, value)
            user.address.save()
        else:
            # Create new address
            address = Address.objects.create(**address_data)
            user.address = address

        # Handle password change
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()
        return user


# Department Management Forms
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name"]


# Job Management Forms
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description"]


# Goal Management Forms
class GoalForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'text',
                'class': 'form-control flatpickr-datetime',
                'data-enable-time': 'true',
                'data-time_24hr': 'true',
                'data-min-date': 'today',
                'data-date-format': 'Y-m-d H:i',
                'placeholder': 'Select date and time',
                'autocomplete': 'off',
            }
        ),
        error_messages={
            'required': 'Please select a due date and time.',
            'invalid': 'Please enter a valid date and time.',
        }
    )

    def __init__(self, *args, **kwargs):
        super(GoalForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = True
        self.fields['description'].widget.attrs.update({
            'rows': 3,
            'style': 'resize: vertical;',
            'placeholder': 'Describe your goal in detail...',
            'class': 'form-control',
        })

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or not description.strip():
            raise forms.ValidationError("Please enter a goal description.")
        return description.strip()

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if not due_date:
            raise forms.ValidationError("Please select a due date and time.")
        if due_date < timezone.now():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due_date

    class Meta:
        model = Goal
        fields = ["description", "due_date"]
        error_messages = {
            'description': {
                'required': "Please enter a goal description.",
            },
        }


# Attendance Management Forms
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["time_in", "time_out", "status"]
        widgets = {
            "time_in": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "time_out": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


# Leave Management Forms
class LeaveForm(forms.ModelForm):
    leave_type = forms.ChoiceField(
        choices=Leave.LEAVE_TYPES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Leave Type",
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Start Date",
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="End Date",
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}),
        label="Reason",
        required=True,
    )

    class Meta:
        model = Leave
        fields = ["leave_type", "start_date", "end_date", "reason"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today for both start and end date
        today = date.today().strftime('%Y-%m-%d')
        self.fields['start_date'].widget.attrs['min'] = today
        self.fields['end_date'].widget.attrs['min'] = today

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        today = date.today()

        if start_date:
            if start_date < today:
                self.add_error('start_date', 'Leave cannot be requested for past dates.')
            
            if end_date and end_date < start_date:
                self.add_error('end_date', 'End date must be after start date.')

        return cleaned_data