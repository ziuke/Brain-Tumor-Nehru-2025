from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import  *



urlpatterns = [
    path('',views.index),
    path('login',views.doLogin),
    path('about/',views.about,name='about'),
    path('user_register', views.user_register, name='user_register'),
    path('doctor_register',views.doctor_register,name='doctor_register'),
    path('forgotpswd/',views.forgotpswd),
    path('logout/',views.logout),
    path('generate_random_password',views.generate_random_password),
    path('reset_password',views.reset_password,name='password_change'),
    path('profile',views.profile),
    path('edit_profile',views.edit_profile),


    path('check_mri/',views.check_mri,name='check_mri'),
    path('prediction_result/<int:prediction_id>/',views.prediction_result,name='prediction_result'),
    path('prediction_history/',views.prediction_history,name='prediction_history'),
    path('delete_prediction/<int:prediction_id>/',views.delete_prediction,name='delete_prediction'),
    
    
   
]
