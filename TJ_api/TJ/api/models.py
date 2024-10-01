from django.db import models
from django_countries.fields import CountryField  
# Create your models here.

class Address(models.Model):
    street = models.CharField(max_length=255)
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
        MANAGER = 'Manager', 'manager'
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    email = models.CharField(max_length=20)
    role = models.CharField(choices=RoleType.choices, default=RoleType.EMPLOYEE)
    date_of_hire = models.DateField()
    job_id = models.OneToOneField(Job, on_delete=models.CASCADE)