from django.shortcuts import render
from .models import User
from rest_framework import generics
from .serializers import UserSerializer

# Create your views here.
# user registration
class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Get Users with employee role
class EmployeeList(generics.ListAPIView):
    queryset = User.objects.filter(role=User.RoleType.EMPLOYEE)


