from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from worker_acc.models import Workers, Rating
from django.db.models import Avg
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from itertools import chain
import random
from .models import SiteVisitRequest, Workers
import json
from django.utils.timezone import now
from worker_profiles.models import Booking, Payment, SiteVisitRequest, SiteVisitPayment, WorkerBankDetail, WorkerTransactionHistory, WorkerWallet, WorkerWithdrawRequest
from user_acc.models import Users
from datetime import datetime, date, timedelta
from django.contrib import messages
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from worker_list.models import WorkerReport, Workers
from django.http import HttpResponse
from worker_list.models import UserReport
from django.utils import timezone
import qrcode
from io import BytesIO
import base64
from decimal import Decimal
def user_notifications(request):
    if "user_id" not in request.session:
        return render(request, "user_acc/user_login.html", {"error": "User not logged in."})

    user = get_object_or_404(Users, id=request.session.get("user_id"))
    today = date.today()


    bookings = Booking.objects.filter(
        user=user,
        worker_notified=True
    ).order_by("-created_at")


    site_visits = SiteVisitRequest.objects.filter(
        user=user,

    ).order_by("-submitted_at")


    for booking in bookings:
        if booking.status == "Accepted" and booking.end_date < today:
            booking.status = "Expired"
            booking.save()


    for visit in site_visits:
        if visit.status == "Accepted" and visit.confirmed_date and visit.confirmed_date < today:
            visit.status = "Expired"
            visit.save()

    return render(request, "worker_profiles/notification.html", {
        "bookings": bookings,
        "site_visits": site_visits,
        "today": today,
    })

def worker_notifications(request):
    if "worker_id" not in request.session:
        return redirect("worker_login")

    worker = get_object_or_404(Workers, id=request.session["worker_id"])

    worker_bookings = Booking.objects.filter(worker=worker, status='Pending')
    site_visit_requests = SiteVisitRequest.objects.filter(worker=worker, status='Pending')

    context = {
        "worker_bookings": worker_bookings,
        "site_visit_requests": site_visit_requests,
    }
    return render(request, "worker_profiles/notificationw.html", context)


def handle_notification(request, notif_type, notif_id):
    if request.method == "POST":
        data = json.loads(request.body)
        action = data.get('action')
        response_message = data.get('response_message')

        if notif_type == "booking":
            booking = get_object_or_404(Booking, id=notif_id)
            if action == "accept":
                booking.status = 'Accepted'
                booking.response_message = response_message
            elif action == "reject":
                booking.status = 'Rejected'
                booking.response_message = response_message
            booking.save()
            return JsonResponse({"success": "Booking updated successfully."})

        elif notif_type == "site_visit":
            visit = get_object_or_404(SiteVisitRequest, id=notif_id)
            if action == "accept":
                visit.status = 'Accepted'
                visit.response_message = response_message
            elif action == "reject":
                visit.status = 'Rejected'
                visit.response_message = response_message
            visit.save()
            return JsonResponse({"success": "Site visit request updated successfully."})

        return JsonResponse({"error": "Invalid request."})

    return JsonResponse({"error": "Invalid method."})

def contact_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, status="Accepted")

    user_id = request.session.get("user_id")
    if not user_id or booking.user.id != user_id:
        return redirect("user_acc:user_login")

    return render(request, "worker_profiles/contact_page.html", {"booking": booking})


@csrf_exempt
def book_worker(request, worker_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

        user_id = request.session.get("user_id")
        if not user_id or "worker_id" in request.session:
            return JsonResponse({"error": "User not logged in."}, status=400)

        user = get_object_or_404(Users, id=user_id)
        worker = get_object_or_404(Workers, id=worker_id)

        start_date_str = data.get("start_date")
        message = data.get("message")
        work_site = data.get("work_site")

        if not start_date_str:
            return JsonResponse({"error": "Please select a starting date."}, status=400)

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format."}, status=400)

        if start_date < datetime.today().date():
            return JsonResponse({"error": "Cannot book a past date."}, status=400)

        end_date = start_date


        existing_bookings = Booking.objects.filter(
            worker=worker,
            status="Accepted",
            start_date__lte=end_date,
            end_date__gte=start_date
        )

        if existing_bookings.exists():
            return JsonResponse({"error": "The selected date is already booked."}, status=400)

        Booking.objects.create(
            user=user,
            worker=worker,
            start_date=start_date,
            end_date=end_date,
            message=message,
            work_site=work_site,
            status="Pending",
        )

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request method."}, status=400)


@csrf_exempt
def update_booking_status(request, booking_id):
    if request.method == "POST":
        worker_id = request.session.get("worker_id")
        if not worker_id:
            return JsonResponse({"error": "Worker not logged in."}, status=403)

        booking = get_object_or_404(Booking, id=booking_id)
        if booking.worker.id != worker_id:
            return JsonResponse({"error": "Unauthorized access."}, status=403)

        try:
            data = json.loads(request.body)
            action = data.get("action")
            response_message = data.get("response_message", "").strip()
        except Exception:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

        if action not in ["accept", "reject"]:
            return JsonResponse({"error": "Invalid action."}, status=400)

        if not response_message:
            return JsonResponse({"error": "Message is required."}, status=400)

        booking.status = "Accepted" if action == "accept" else "Rejected"
        booking.worker_response = response_message
        booking.worker_notified = True



        booking.save()
        return JsonResponse({"success": "Booking status updated and user notified."})

    return JsonResponse({"error": "Invalid request."}, status=400)


@csrf_exempt
def update_site_visit_status(request, visit_id):
    if request.method == "POST":
        worker_id = request.session.get("worker_id")
        if not worker_id:
            return JsonResponse({"error": "Worker not logged in."}, status=403)

        visit = get_object_or_404(SiteVisitRequest, id=visit_id)
        if visit.worker.id != worker_id:
            return JsonResponse({"error": "Unauthorized access."}, status=403)

        try:
            data = json.loads(request.body)
            action = data.get("action")
            response_message = data.get("response_message", "").strip()
            confirmed_date = data.get("confirmed_date")
        except Exception:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

        if action not in ["accept", "reject"]:
            return JsonResponse({"error": "Invalid action"}, status=400)

        if not response_message:
            return JsonResponse({"error": "Message is required."}, status=400)

        visit.status = "Accepted" if action == "accept" else "Rejected"
        visit.worker_response = response_message

        if action == "accept":
            if not confirmed_date:
                return JsonResponse({"error": "Confirmed date is required for acceptance."}, status=400)
            visit.confirmed_date = confirmed_date
        else:
            visit.confirmed_date = None

        visit.save()
        return JsonResponse({"success": "Site visit status updated successfully."})

    return JsonResponse({"error": "Invalid request method."}, status=400)

def worker_profile(request, worker_id):
    if "user_id" not in request.session:
        return redirect("user_acc:user_login")

    user = get_object_or_404(Users, id=request.session["user_id"])
    worker = get_object_or_404(Workers, id=worker_id)
    ratings = Rating.objects.filter(worker=worker)
    avg_rating = ratings.aggregate(Avg('rating_value'))['rating_value__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else "No ratings yet"

    return render(request, "worker_profiles/worker_profile.html", {
        "user": user,
        "worker": worker,
        "ratings": ratings,
        "avg_rating": avg_rating,
        "today": date.today()
    })

def worker_profiles(request, worker_id):
    if "user_id" not in request.session:
        return redirect("user_acc:user_login")

    user = get_object_or_404(Users, id=request.session["user_id"])
    worker = get_object_or_404(Workers, id=worker_id)

    return render(request, "worker_profiles/worker_profile.html", {
        "user": user,
        "worker": worker,
        "today": date.today()
    })

def submit_rating(request, booking_id):
    if "user_id" not in request.session:
        return redirect("user_acc/user_login.html")

    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        worker = booking.worker
        user = get_object_or_404(Users, id=request.session["user_id"])

        if Rating.objects.filter(user=user, booking=booking).exists():
            messages.warning(request, "You've already rated this worker for this booking.")
            return redirect('worker_profiles:contact_page', booking.id)

        rating_value_raw = request.POST.get('rating_value')
        if rating_value_raw is None:
            messages.error(request, "Rating value is missing.")
            return redirect('worker_profiles:contact_page', booking.id)

        try:
            rating_value = float(rating_value_raw)
        except ValueError:
            messages.error(request, "Invalid rating value.")
            return redirect('worker_profiles:contact_page', booking.id)

        Rating.objects.create(
            worker=worker,
            user=user,
            rating_value=rating_value,
            booking=booking
        )

        messages.success(request, "Your rating has been submitted.")
        return redirect('worker_profiles:contact_page', booking.id)

    return redirect('worker_profiles:contact_page', booking_id)

def worker_bookings(request):
    worker_id = request.session.get('worker_id')
    today = date.today()

    bookings = Booking.objects.filter(
        worker_id=worker_id,
        status='Accepted',
        payment__payment_done=True,
        end_date__gte=today
    ).order_by('start_date')

    for booking in bookings:
        booking.is_today = booking.start_date <= today <= booking.end_date

    site_visits = SiteVisitRequest.objects.filter(
        worker_id=worker_id,
        confirmed_date__gte=today,
        status__in=['Accepted', 'Completed'],
        site_visit_payment__payment_done=True,
        site_visit_payment__admin_approved=True
    ).order_by('confirmed_date')

    for visit in site_visits:
        visit.is_today = visit.confirmed_date == today

    return render(request, 'worker_profiles/worker_bookings.html', {
        'bookings': bookings,
        'site_visits': site_visits,
        'today': today,
    })
def my_profile(request):
    worker_id = request.session.get("worker_id")

    if not worker_id:
        return redirect('loginw')

    try:
        worker = Workers.objects.get(id=worker_id)
    except Workers.DoesNotExist:
        return render(request, "worker_profiles/my_profile.html", {"error": "Worker not found"})

    if request.method == 'POST':
        try:

            worker.full_name = request.POST.get('full_name', '').strip()
            worker.gender = request.POST.get('gender', '').strip()
            worker.mobile = request.POST.get('mobile', '').strip()
            worker.email = request.POST.get('email', '').strip()
            worker.state = request.POST.get('state', '').strip()
            worker.district = request.POST.get('district', '').strip()
            worker.job_category = request.POST.get('job_category', '').strip()


            EmailValidator()(worker.email)


            worker.experience = int(request.POST.get('experience', 0))
            worker.daily_wage = float(request.POST.get('daily_wage', 0))
            worker.working_hours = int(request.POST.get('working_hours', 0))


            if 'profile_image' in request.FILES:
                worker.profile_image = request.FILES['profile_image']

            worker.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('my_profile')

        except ValidationError:
            messages.error(request, 'Invalid email format.')
        except ValueError:
            messages.error(request, 'Please enter valid numeric values for Experience, Daily Wage, and Working Hours.')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')

    return render(request, "worker_profiles/my_profile.html", {"worker": worker})

def user_profile(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect('login')

    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return render(request, "worker_profiles/my_profileuser.html", {"error": "User not found"})

    if request.method == 'POST':
        try:

            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.mobile = request.POST.get('mobile', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.state = request.POST.get('state', '').strip()
            user.district = request.POST.get('district', '').strip()


            EmailValidator()(user.email)

            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('my_profileuser')

        except ValidationError:
            messages.error(request, 'Invalid email format.')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')

    return render(request, "worker_profiles/my_profileuser.html", {"user": user})

def report_worker(request, worker_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("user_acc:user_login")

    reporter = get_object_or_404(Users, id=user_id)
    worker = get_object_or_404(Workers, id=worker_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')

        WorkerReport.objects.create(
            reporter=reporter,
            worker=worker,
            reason=reason,
            description=description
        )

        return render(request, 'worker_profiles/report_worker.html', {
            'worker': worker,
            'success': True
        })

    return render(request, 'worker_profiles/report_worker.html', {
        'worker': worker
    })

def submit_report(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        reason = request.POST.get("reason")
        description = request.POST.get("description")

        reporter_id = request.session.get("worker_id")
        if not reporter_id:
            return redirect("worker_acc:worker_login")

        reporter = get_object_or_404(Workers, id=reporter_id)
        user = get_object_or_404(Users, id=user_id)

        UserReport.objects.create(
            reporter=reporter,
            user=user,
            reason=reason,
            description=description
        )

        messages.success(request, "User report submitted successfully.")
        return redirect("worker_profiles:worker_bookings")

    return redirect("worker_profiles:worker_bookings")

def user_booking(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("user_acc:user_login")

    user = get_object_or_404(Users, id=user_id)
    today = timezone.now().date()

    pending_bookings = Booking.objects.filter(
        user=user,
        status='Accepted'
    ).filter(
        Q(payment__isnull=True) | Q(payment__payment_done=False)
    ).order_by('start_date')

    accepted_bookings = Booking.objects.filter(
        user=user,
        status__in=['Accepted', 'Paid'],
        payment__payment_done=True
    ).order_by('start_date')

    for booking in accepted_bookings:
        booking.is_today = booking.start_date <= today <= booking.end_date

    context = {
        'pending_bookings': pending_bookings,
        'accepted_bookings': accepted_bookings,
    }
    return render(request, 'worker_profiles/user_bookings.html', context)

def payment_qr(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    worker = booking.worker
    wage = worker.daily_wage
    days = (booking.end_date - booking.start_date).days + 1

    DecimalType = type(wage)
    worker_payment = wage * days
    platform_fee = worker_payment * DecimalType('0.05')
    total_amount = worker_payment + platform_fee

    if request.method == "POST":
        upi_transaction_id = request.POST.get("upiTransactionId")
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': total_amount,
                'upi_transaction_id': upi_transaction_id
            }
        )
        if not created:
            payment.upi_transaction_id = upi_transaction_id
            payment.amount = total_amount
            payment.save()
        return redirect("worker_profiles:user_booking")

    upi_id = "rummoozzofficial-2@okicici"
    name = "Worker-finder"
    note = f"Booking {worker.full_name}"

    upi_link = (
        f"upi://pay?pa={upi_id}&pn={name}&am={int(total_amount)}&cu=INR&tn={note}"
    )

    qr = qrcode.make(upi_link)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render(request, "worker_profiles/payment.html", {
        "qr_code": img_str,
        "total_amount": int(total_amount),
        "worker_payment": int(worker_payment),
        "platform_fee": int(platform_fee),
        "worker": worker,
        "booking": booking,
    })
@csrf_exempt
def submit_transaction(request, booking_id):
    if request.method == "POST":
        upi_id = request.POST.get("upiTransactionId")
        booking = Booking.objects.get(id=booking_id)
        if upi_id:
            booking.upi_transaction_id = upi_id
            booking.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

def payment_success(request, booking_id):
    booking = Booking.objects.get(id=booking_id)


    booking.verification_code = str(random.randint(100000, 999999))
    booking.save()

    messages.success(request, f"Payment successful! Your verification code is {booking.verification_code}")
    return redirect("user_bookings_page")

def submit_reportw(request):
    if request.method == "POST":
        worker_id = request.POST.get("worker_id")
        reason = request.POST.get("reason")
        description = request.POST.get("description")

        reporter_id = request.session.get("user_id")
        if not reporter_id:
            return redirect("user_acc:user_login")

        reporter = get_object_or_404(Users, id=reporter_id)
        worker = get_object_or_404(Workers, id=worker_id)


        WorkerReport.objects.create(
            reporter=reporter,
            worker=worker,
            reason=reason,
            description=description
        )


        return redirect("afterlogin")

    return redirect("afterlogin")

def verify_otp(request, booking_id):
    if request.method == 'POST':
        otp_input = request.POST.get('otp_input')
        booking = get_object_or_404(Booking, id=booking_id, worker_id=request.session.get('worker_id'))
        if booking.verification_code == otp_input:
            booking.worker_marked_completed = True
            booking.save()


            worker = booking.worker
            amount = booking.payment.amount

            wallet, created = WorkerWallet.objects.get_or_create(worker=worker)
            wallet.total_earnings += amount
            wallet.available_balance += amount
            wallet.save()


            WorkerTransactionHistory.objects.create(
                worker=worker,
                transaction_type='earning',
                amount=amount,
                description=f'Earning for booking #{booking.id}'
            )

            messages.success(request, "Work marked as completed. Amount added to your wallet.")
        else:
            messages.error(request, "Incorrect OTP. Please check with the user.")
    return redirect('worker_profiles:worker_bookings')


def request_site_visit(request, worker_id):
    if request.method == 'POST':
        if "user_id" not in request.session:
            return JsonResponse({"error": "User not logged in."}, status=401)

        bio = request.POST.get('bio')
        date1 = request.POST.get('date1')
        date2 = request.POST.get('date2')
        date3 = request.POST.get('date3')
        location = request.POST.get('location')

        worker = get_object_or_404(Workers, id=worker_id)
        user = get_object_or_404(Users, id=request.session['user_id'])

        SiteVisitRequest.objects.create(
            user=user,
            worker=worker,
            preferred_date1=date1,
            preferred_date2=date2,
            preferred_date3=date3,
            location=location,
            bio=bio
        )

        return JsonResponse({"success": True, "message": "Site visit request submitted successfully."})

    return JsonResponse({"error": "Invalid method."}, status=400)


def site_visit_payment_qr(request, visit_id):
    visit = SiteVisitRequest.objects.get(id=visit_id)
    worker_payment = Decimal('149')
    platform_fee = worker_payment * Decimal('0.05')
    total_amount = worker_payment + platform_fee

    if request.method == "POST":
        upi_transaction_id = request.POST.get("upiTransactionId")
        payment, created = SiteVisitPayment.objects.get_or_create(
            site_visit=visit,
            defaults={
                'amount': total_amount,
                'upi_transaction_id': upi_transaction_id
            }
        )
        if not created:
            payment.upi_transaction_id = upi_transaction_id
            payment.amount = total_amount
            payment.save()
        return redirect("worker_profiles:user_notifications")

    upi_id = "rummoozzofficial-2@okicici"
    name = "Worker-Finder"
    note = f"Site Visit {visit.worker.full_name}"

    upi_link = (
        f"upi://pay?pa={upi_id}&pn={name}&am={int(total_amount)}&cu=INR&tn={note}"
    )

    qr = qrcode.make(upi_link)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render(request, "worker_profiles/payment.html", {
        "qr_code": img_str,
        "total_amount": int(total_amount),
        "worker_payment": int(worker_payment),
        "platform_fee": int(platform_fee),
        "worker": visit.worker,
        "visit": visit,
    })

@csrf_exempt
def submit_site_visit_transaction(request, visit_id):
    if request.method == "POST":
        upi_id = request.POST.get("upiTransactionId")
        visit = SiteVisitRequest.objects.get(id=visit_id)
        if upi_id:
            visit.upi_transaction_id = upi_id
            visit.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

def site_visit_payment_success(request, visit_id):
    visit = SiteVisitRequest.objects.get(id=visit_id)

    visit.verification_code = str(random.randint(100000, 999999))
    visit.save()

    messages.success(request, f"Payment successful! Your verification code is {visit.verification_code}")
    return redirect("worker_profiles:user_site_visits")

def add_bank_details(request):
    worker_id = request.session.get('worker_id')
    worker = Workers.objects.get(id=worker_id)

    if hasattr(worker, 'workerbankdetail'):
        return redirect('worker_profiles:worker_wallet')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        account_number = request.POST.get('account_number')
        ifsc_code = request.POST.get('ifsc_code')

        WorkerBankDetail.objects.create(
            worker=worker,
            full_name=full_name,
            account_number=account_number,
            ifsc_code=ifsc_code
        )

        return redirect('worker_profiles:worker_wallet')

    return render(request, 'worker_profiles/add_bank_details.html')

def worker_wallet(request):
    worker_id = request.session.get('worker_id')
    worker = Workers.objects.get(id=worker_id)

    try:
        bank_details = WorkerBankDetail.objects.get(worker=worker)
    except WorkerBankDetail.DoesNotExist:
        return redirect('worker_profiles:add_bank_details')


    wallet, created = WorkerWallet.objects.get_or_create(worker=worker)


    transactions = WorkerTransactionHistory.objects.filter(worker=worker).order_by('-timestamp')

    context = {
        'wallet': wallet,
        'bank_details': bank_details,
        'transactions': transactions,
    }
    return render(request, 'worker_profiles/worker_wallet.html', context)

def withdraw_request(request):
    worker_id = request.session.get('worker_id')
    worker = Workers.objects.get(id=worker_id)

    try:
        bank_detail = WorkerBankDetail.objects.get(worker=worker)
    except WorkerBankDetail.DoesNotExist:
        bank_detail = None

    # Ensure wallet exists
    wallet, _ = WorkerWallet.objects.get_or_create(worker=worker)
    available_balance = wallet.available_balance or Decimal('0.00')
    MIN_WITHDRAW_AMOUNT = Decimal('500.00')

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', '0'))
        bank_name = request.POST.get('bank_name')
        bank_account_number = request.POST.get('bank_account_number')
        ifsc_code = request.POST.get('ifsc_code')
        entered_password = request.POST.get('password')

        # Validate password
        if not check_password(entered_password, worker.password):
            messages.error(request, "Incorrect password. Please try again.")
            return redirect('worker_profiles:withdraw_request')


        if amount < MIN_WITHDRAW_AMOUNT:
            messages.error(request, f"Minimum withdrawal amount is ₹{MIN_WITHDRAW_AMOUNT}.")
            return redirect('worker_profiles:withdraw_request')


        if amount > available_balance:
            messages.error(request, "Insufficient wallet balance.")
            return redirect('worker_profiles:withdraw_request')


        WorkerWithdrawRequest.objects.create(
            worker=worker,
            amount=amount,
            bank_account_name=bank_name,
            bank_account_number=bank_account_number,
            ifsc_code=ifsc_code,
            status='pending'
        )

        # Save or update bank details
        if bank_detail:
            bank_detail.bank_account_name = bank_name
            bank_detail.bank_account_number = bank_account_number
            bank_detail.ifsc_code = ifsc_code
            bank_detail.save()
        else:
            WorkerBankDetail.objects.create(
                worker=worker,
                bank_account_name=bank_name,
                bank_account_number=bank_account_number,
                ifsc_code=ifsc_code
            )

        messages.success(request, "Withdrawal request submitted successfully. Admin will review it shortly.")
        return redirect('worker_profiles:worker_wallet')

    context = {
        'worker': worker,
        'bank_detail': bank_detail,
        'available_balance': available_balance,
        'min_withdraw': MIN_WITHDRAW_AMOUNT,
    }
    return render(request, 'worker_profiles/withdraw_request.html', context)

def sitevisit_contact(request, visit_id):
    visit = get_object_or_404(SiteVisitRequest, id=visit_id, status="Accepted")

    user_id = request.session.get("user_id")
    if not user_id or visit.user.id != user_id:
        return redirect("user_acc:user_login")

    return render(request, "worker_profiles/sitevisit_contact.html", {"visit": visit})


def verify_otp_site(request, visit_id):
    if request.method == 'POST':
        otp_input = request.POST.get('otp_input')
        visit = get_object_or_404(SiteVisitRequest, id=visit_id, worker_id=request.session.get('worker_id'))
        if visit.verification_code == otp_input and not visit.worker_marked_completed:
            visit.worker_marked_completed = True
            visit.status = 'Completed'
            visit.save()


            worker = visit.worker
            amount = visit.site_visit_payment.amount

            wallet, created = WorkerWallet.objects.get_or_create(worker=worker)
            wallet.total_earnings += amount
            wallet.available_balance += amount
            wallet.save()


            WorkerTransactionHistory.objects.create(
                worker=worker,
                transaction_type='earning',
                amount=amount,
                description=f'Earning for Site-Visit #{visit.id}'
            )

            messages.success(request, "Work marked as completed. Amount added to your wallet.")
        else:
            messages.error(request, "Incorrect OTP. Please check with the user.")
    return redirect('worker_profiles:worker_bookings')




