# api/urls.py (app-level URLs)

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.landing_view, name="landing"),
    # Authentication URLs
    path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("classify/", views.find_user_view, name="classify"),
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject_user/<int:user_id>/', views.reject_user, name='reject_user'),

    # User URLs
    path("profile/", views.profile, name="profile"),
    # jobs and department URLs
    path('jobs/', views.jobs, name='jobs'),
    path('add_job/', views.add_job, name='add_job'),
    path('add_department/', views.add_department, name='add_department'),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('delete_department/<int:department_id>/', views.delete_department, name='delete_department'),
    # Goal URLs
    path("goals/", views.goal_list, name="goals"),
    path("goals/add/", views.add_goal, name="add_goal"),
    path("goals/<int:pk>/edit/", views.edit_goal, name="edit_goal"),
    path("goals/<int:pk>/delete/", views.delete_goal, name="delete_goal"),
    # Attendance URLs
    path("attendance/", views.attendance, name="attendance"),
    path("attendance/mark", views.mark_attendance, name="mark_attendance"),
    path("attendance/employee", views.employee_attendance, name="employee_attendance"),
    path("attendance/mark_face", views.mark_attendance_face , name="mark_attendance_face"),
    # Leave URLs
    path("leaves/", views.leave_list, name="leaves"),
    path('leaves/<int:pk>/edit/', views.edit_leave, name='edit_leave'),
    path("leaves/request/", views.request_leave, name="request_leave"),
    path("leaves/<int:pk>/", views.leave_detail, name="leave_detail"),
    path("leaves/<int:pk>/delete/", views.delete_leave, name="delete_leave"),
    path('approve_leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject_leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
