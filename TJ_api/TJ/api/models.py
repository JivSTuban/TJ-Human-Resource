import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from PIL import Image

# Department Related Models
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Job Related Models
class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.department}"


# Address Related Models
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"


# User Related Models
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 'APPROVED')
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("EMPLOYEE", "Employee"),
        ("MANAGER", "Manager"),
    ]

    STATUS_CHOICES = [
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("PENDING", "Pending"),
    ]

    # Use email instead of username
    username = None  # Remove the username field entirely
    email = models.EmailField(_("email address"), unique=True)

    # Additional fields
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.OneToOneField(
        Address, on_delete=models.CASCADE, blank=True, null=True
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="EMPLOYEE")
    date_of_hire = models.DateField(blank=True, null=True)
    profile_path = CloudinaryField('profile_picture', folder='profiles', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)

    # Override the groups field
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name=_("groups"),
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    # Override the user_permissions field
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name=_("user permissions"),
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "date_of_hire"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # If this is a new user or the profile picture has changed
        if self.pk is None or (
            self.pk and User.objects.filter(pk=self.pk).exists() and 
            User.objects.get(pk=self.pk).profile_path != self.profile_path
        ):
            # Import and invalidate cache only when needed to avoid circular imports
            from .face_recognition_utils import invalidate_face_encodings_cache
            invalidate_face_encodings_cache()
            
        # Check if the user is a superuser
        if self.is_superuser:
            self.status = "APPROVED"
            self.role = "ADMIN"

        super().save(*args, **kwargs)


# Log Related Models
class Log(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    photo = CloudinaryField('photo', folder='attendance_logs')
    is_correct = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile} - {self.created.strftime('%Y-%m-%d %H:%M:%S')}"

    def save(self, *args, **kwargs):
        # Set options for Cloudinary upload
        options = {
            'quality': 95,  # High quality
            'width': 800,   # Max width
            'height': 800,  # Max height
            'crop': 'limit',  # Resize without cropping
            'folder': 'attendance_logs'  # Cloudinary folder
        }
        
        # If this is a new photo being uploaded
        if self.photo and hasattr(self.photo, 'file'):
            # The CloudinaryField will automatically handle the upload with our options
            self.photo.options.update(options)
        
        super().save(*args, **kwargs)


# Goal Related Models
class Goal(models.Model):
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Goal for {self.user}: due {self.due_date}"


# Attendance Related Models
class Attendance(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LATE", "Late"),
        ("HALF_DAY", "Half Day"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "date"]

    def __str__(self):
        return f"{self.user} - {self.date} - {self.status}"


# Leave Related Models
class Leave(models.Model):
    LEAVE_TYPES = [
        ("ANNUAL", "Annual Leave"),
        ("SICK", "Sick Leave"),
        ("PARENTAL", "Parental Leave"),
        ("UNPAID", "Unpaid Leave"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user} - {self.leave_type} ({self.start_date} to {self.end_date})"