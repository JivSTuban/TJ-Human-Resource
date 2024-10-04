from django.db import models
from django_countries.fields import CountryField  
from django.core.exceptions import ValidationError
# Create your models here.

class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = CountryField()

class Department(models.Model):
    name = models.CharField(max_length=100)

class Job(models.Model):
    job_title = models.CharField(max_length=50)
    job_description = models.TextField()
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)

class User(models.Model):
    class RoleType(models.TextChoices):
        EMPLOYEE = 'employee', 'Employee'
        MANAGER = 'manager', 'Manager'
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    email = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=RoleType.choices, default=RoleType.EMPLOYEE)
    date_of_hire = models.DateField()
    job_id = models.OneToOneField(Job, on_delete=models.CASCADE)

class PerformanceReview(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    employee = models.ForeignKey(User, on_delete=models.CASCADE) # The employee being rated
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    review_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'rater')

    def clean(self):
        if self.employee.role != User.RoleType.EMPLOYEE:
            raise ValidationError('The person being rated must have the employee role.')
        if self.rater.role != User.RoleType.EMPLOYEE:
            raise ValidationError('The rater must have the employee role.')

    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs)
