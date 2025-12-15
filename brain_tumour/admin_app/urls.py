from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import MyModelListView
from .views import *


urlpatterns = [
    path('vw_users/<int:usertype>/',MyModelListView.as_view(), name='model_list'),
    path('doctor_approval_list', views.doctor_approval_list, name='doctor_approval_list'),
    path('reject_reason/<int:id>', views.reject_reason, name='reject_reason'),
   
]