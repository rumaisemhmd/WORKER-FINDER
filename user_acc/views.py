from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Users
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import (never_cache)

@never_cache
def user_login(request):
    if request.session.get("user_id"):
        return redirect("afterlogin")
    if request.method == "POST":
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")

        try:
            user = Users.objects.get(mobile=mobile)
            if check_password(password, user.password):
                if request.session.get("worker_id"):
                    request.session.flush()

                request.session["user_id"] = user.id

                request.session.modified = True

                print("Login success - user_id stored:", request.session.get("user_id"))
                return redirect("afterlogin")
            else:
                return render(request, "user_acc/login.html", {"error": "Invalid password"})
        except Users.DoesNotExist:
            return render(request, "user_acc/login.html", {"error": "Invalid mobile number"})

    return render(request, "user_acc/login.html")
def user_logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect("login")

def registered(request):
    return render(request,"signup.html")
def afterlogin(request):
    return render(request,"afterlogin.html")
def register_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        district = request.POST.get('district')
        state = request.POST.get('state')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')


        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('registered')

        if Users.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('registered')
        if Users.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered!")
            return redirect('registered')


        user = Users(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            district=district,
            state=state,
            password=make_password(password)
        )
        user.save()
        print("User Created!")
        return redirect('login')
    else:
        return render(request,'signup.html')