# api/urls.py (app-level URLs)

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication URLs
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # User URLs
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/<int:pk>/edit/', views.edit_department, name='edit_department'),
    
    # Job URLs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/add/', views.add_job, name='add_job'),
    path('jobs/<int:pk>/edit/', views.edit_job, name='edit_job'),
    
    # Goal URLs
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/<int:pk>/edit/', views.edit_goal, name='edit_goal'),
    
    # Attendance URLs
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    
    # Leave URLs
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/request/', views.request_leave, name='request_leave'),
    path('leaves/<int:pk>/', views.leave_detail, name='leave_detail'),
]