from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth import logout
from .models import Workers, Users
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import (Workers, Users, InterviewRequest)
from django.http import HttpResponse
from django.views.decorators.cache import (never_cache)


def interview_request(request):
    if request.method == 'POST':
        print("Form received:", request.POST)  # Step 1 check

        try:
            InterviewRequest.objects.create(
                full_name=request.POST.get('full_name'),
                age=request.POST.get('age'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                gender=request.POST.get('gender'),
                job_role=request.POST.get('job_role'),
                experience=request.POST.get('experience'),
                district=request.POST.get('district'),
                state=request.POST.get('state'),
            )
            print("Saved successfully!")  # Step 2 check
        except Exception as e:
            print("Error while saving:", e)  # Step 3 check

        return render(request, 'home', {'submitted': True})

    return render(request, 'worker_profiles/interview_request.html')

@never_cache
def worker_login(request):
    if request.session.get("worker_id"):
        return redirect("afterloginw")
    if request.method == "POST":
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")

        try:
            worker = Workers.objects.get(mobile=mobile)

            if not worker.is_approved:
                return render(request, "loginw.html", {"error": "Your account is pending admin approval"})

            if check_password(password, worker.password):

                if request.session.get("user_id"):
                    request.session.flush()

                request.session["worker_id"] = worker.id
                request.session["worker_name"] = worker.full_name
                request.session.modified = True

                print(f"✅ LOGIN SUCCESS: Stored worker_id={worker.id} in session")
                return redirect("afterloginw")
            else:
                return render(request, "loginw.html", {"error": "Invalid password"})
        except Workers.DoesNotExist:
            return render(request, "loginw.html", {"error": "Worker not found"})

    return render(request, "loginw.html")




def worker_logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect("worker_login")

def register_success(request):
    if request.method == "POST":
        fullname = request.POST.get("fullName")
        bio = request.POST.get("bio")
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        confirmpassword = request.POST.get("confirmPassword")
        jobcategory = request.POST.get("jobCategory")
        experience = request.POST.get("experience")
        workinghours = request.POST.get("workingHours")
        dailywage = request.POST.get("dailyWage")
        state = request.POST.get("state")
        district = request.POST.get("district")


        aadhar = request.FILES.get("aadhar")
        proof = request.FILES.get("proof")
        profile_image = request.FILES.get("profile_image")


        if password != confirmpassword:
            messages.error(request, "Passwords do not match.")
            return redirect("worker_acc:register")


        if Workers.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("worker_acc:register")
        if Workers.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return redirect("worker_acc:register")


        worker = Workers(
            full_name=fullname,
            bio=bio,
            age=age,
            gender=gender,
            email=email,
            mobile=mobile,
            password=make_password(password),
            job_category=jobcategory,
            experience=experience,
            working_hours=workinghours,
            daily_wage=dailywage,
            state=state,
            district=district,
            profile_image=profile_image,
            aadhar=aadhar,
            proof=proof,
            is_approved=False
        )
        worker.save()

        messages.success(request, "Registration submitted! Wait for admin approval.")
        return redirect("worker_acc:loginw")

    return render(request, "worker_acc/register.html")



def afterloginw(request):
    return render(request, "afterloginw.html")


def register(request):
    return render(request, "register.html")

def loginw(request):
    return render(request, "loginw.html")