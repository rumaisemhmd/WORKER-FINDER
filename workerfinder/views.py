
from django.shortcuts import render, redirect

from django.contrib import messages

# Create your views here.
def home(request):
    return render(request,"index.html")
def services(request):
    return render(request,"services.html")
def servicesafter(request):
    return render(request,"servicesafter.html")
def about(request):
    return render(request,"about.html")
def aboutafter(request):
    return render(request,"aboutafter.html")
def aboutafterW(request):
    return render(request,"aboutafterW.html")
def login(request):
    return render(request,"login.html")
def loginw(request):
    return render(request,"loginw.html")
def afterlogin(request):
    return render(request,"afterlogin.html")
def afterloginw(request):
    return render(request,"afterloginw.html")
def signup(request):
    return render(request,"signup.html")
def signupw(request):
    return render(request,"signupw.html")
def editprofile(request):
    return render(request,"editprofile.html")
def helpcenter(request):
    return render(request,"helpcenter.html")
def register(request):
    return render(request,"register.html")
def privacy_policy(request):
    return render(request,"privacy_policy.html")
def interview_request(request):
    return render(request,"interview_request.html")


