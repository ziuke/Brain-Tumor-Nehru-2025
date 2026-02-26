from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import *



urlpatterns = [
    path('', views.index),
    path('login', views.doLogin),
    path('about/', views.about, name='about'),
    path('user_register', views.user_register, name='user_register'),
    path('doctor_register', views.doctor_register, name='doctor_register'),
    path('forgotpswd/', views.forgotpswd),
    path('logout/', views.logout),
    path('generate_random_password', views.generate_random_password),
    path('reset_password', views.reset_password, name='password_change'),
    path('profile', views.profile_view, name='profile'),
    path('edit_profile', views.edit_profile),
    path('change_password', views.change_password, name='change_password'),
    path('user/dashboard', views.user_dashboard, name='user_dashboard'),
    path('doctor/dashboard', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile', views.doctor_profile_edit, name='doctor_profile_edit'),
    path('doctor/availability', views.doctor_availability_list, name='doctor_availability_list'),
    path('doctor/availability/add', views.doctor_availability_add, name='doctor_availability_add'),
    path('doctor/availability/delete/<int:availability_id>/', views.doctor_availability_delete, name='doctor_availability_delete'),
    path('appointment/book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('appointment/book/<int:doctor_id>/<int:prediction_id>/', views.book_appointment, name='book_appointment_prediction'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointment/<int:appointment_id>/status/<str:status>/', views.appointment_update_status, name='appointment_update_status'),
    path('appointment/<int:appointment_id>/chat', views.send_chat_message, name='send_chat_message'),
    path('appointment/<int:appointment_id>/document', views.upload_document, name='upload_document'),
    path('appointment/<int:appointment_id>/treatment', views.update_treatment_plan, name='update_treatment_plan'),
    path('appointment/<int:appointment_id>/feedback', views.submit_feedback, name='submit_feedback'),
    path('payment/create/<int:appointment_id>/', views.create_payment, name='create_payment'),
    path('payment/success', views.payment_success, name='payment_success'),
    path('queries', views.user_queries, name='user_queries'),
    path('doctor/queries', views.doctor_queries, name='doctor_queries'),
    path('doctor/queries/answer/<int:query_id>/', views.answer_query, name='answer_query'),
    path('medical_history/edit', views.medical_history_edit, name='medical_history_edit'),
    path('medical_history/view/<int:patient_id>/', views.medical_history_view, name='medical_history_view'),
    path('notifications', views.notifications_list, name='notifications_list'),
    path('check_mri/', views.check_mri, name='check_mri'),
    path('prediction_result/<int:prediction_id>/', views.prediction_result, name='prediction_result'),
    path('prediction_history/', views.prediction_history, name='prediction_history'),
    path('delete_prediction/<int:prediction_id>/', views.delete_prediction, name='delete_prediction'),
]
