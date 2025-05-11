from django.contrib import admin
from django.urls import path
from django.urls import path, include
from . import views

app_name = "worker_acc"

urlpatterns = [
    path('register/',views.register,name="register"),
    path('afterloginw/',views.afterloginw,name="afterloginw"),
    path('register/success/',views.register_success,name="register_success"),
    path('worker-login/', views.worker_login, name="worker_login"),
    path("worker-logout/",views.worker_logout,name='worker_logout'),
    path("loginw/",views.loginw,name='loginw'),
    path("work-details/", views.register_success, name="work_details"),
    path('interview-request/', views.interview_request, name='interview_request'),


]

