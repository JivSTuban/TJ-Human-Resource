import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
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
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

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
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.OneToOneField(
        Address, on_delete=models.CASCADE, blank=True, null=True
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="EMPLOYEE")
    date_of_hire = models.DateField(blank=True, null=True)
    profile_path = models.ImageField(null=True, blank=True)
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
    REQUIRED_FIELDS = ["first_name", "last_name", "date_of_hire", "password"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    
    def save(self, *args, **kwargs):
         # Check if the user is a superuser
        if self.is_superuser:
            self.status = "APPROVED"
            self.role = "ADMIN"

        # Check if the profile picture has changed
        if self.pk:
            old_profile = User.objects.get(pk=self.pk)
            if old_profile.profile_path and old_profile.profile_path != self.profile_path:
                # Delete the old photo if it exists
                old_profile_path = os.path.join(settings.MEDIA_ROOT, old_profile.profile_path.name)
                if os.path.exists(old_profile_path):
                    os.remove(old_profile_path)

                # Rename the uploaded image to the current date and time
                if self.profile_path:
                    ext = os.path.splitext(self.profile_path.name)[1]
                    new_filename = timezone.now().strftime('%Y%m%d%H%M%S') + ext
                    self.profile_path.name = os.path.join('profiles', new_filename)

        super().save(*args, **kwargs)

        # Resize the image if it exists
        if self.profile_path and os.path.exists(self.profile_path.path):
            try:
                img = Image.open(self.profile_path.path)
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_path.path)
            except FileNotFoundError:
                print(f"File not found: {self.profile_path.path}")


# Log Related Models
class Log(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    photo = models.ImageField(upload_to='logs')
    is_correct = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    

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