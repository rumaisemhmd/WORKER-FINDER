from django.urls import path
from . import views
urlpatterns=[
    path('',views.home,name='home'),
    path('services/',views.services,name='services'),
    path('servicesafter/',views.servicesafter,name='servicesafter'),
    path('about/',views.about,name='about'),
    path('aboutafter/',views.aboutafter,name='aboutafter'),
    path('aboutafterW/',views.aboutafterW,name='aboutafterW'),
    path('login/',views.login,name='login'),
    path('loginw/',views.loginw,name='loginw'),
    path('afterlogin/',views.afterlogin,name='afterlogin'),
    path('worker/afterloginw/',views.afterloginw,name='afterloginw'),
    path('signup/',views.signup,name='signup'),
    path('signupw/',views.signupw,name='signupw'),
    path('editprofile/',views.editprofile,name='editprofile'),
    path('helpcenter/',views.helpcenter,name='helpcenter'),
    path('register/', views.register, name='register'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('interview-request/', views.interview_request, name='interview_request'),


]