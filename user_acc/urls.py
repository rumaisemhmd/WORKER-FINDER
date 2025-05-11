from django.urls import path, include
from . import views
from django.contrib import admin


urlpatterns = [
    path('afterlogin/',views.afterlogin,name="afterlogin"),
    path('register_user/',views.register_user,name="register_user"),
    path('registered',views.registered,name="registered"),
    path('user-login/', views.user_login, name="user_login"),
    path("user-logout/",views.user_logout,name='user_logout'),


]


































