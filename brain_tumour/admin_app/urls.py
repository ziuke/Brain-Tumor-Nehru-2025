from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import MyModelListView
from .views import *


urlpatterns = [
    path('vw_users/<int:usertype>/', MyModelListView.as_view(), name='model_list'),
    path('admins/dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('doctor_approval_list', views.doctor_approval_list, name='doctor_approval_list'),
    path('reject_reason/<int:id>', views.reject_reason, name='reject_reason'),
    path('admins/doctors', views.admin_doctor_list, name='admin_doctor_list'),
    path('admins/doctors/create', views.admin_doctor_create, name='admin_doctor_create'),
    path('admins/users', views.admin_user_list, name='admin_user_list'),
    path('admins/toggle/<int:user_id>/', views.admin_toggle_active, name='admin_toggle_active'),
    path('admins/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admins/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admins/feedbacks', views.admin_feedback_list, name='admin_feedback_list'),
    path('admins/reports', views.admin_reports, name='admin_reports'),
]
