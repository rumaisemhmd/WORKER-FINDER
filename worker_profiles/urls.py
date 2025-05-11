from django.urls import path
from . import views

app_name = "worker_profiles"

urlpatterns = [
    path('worker/<int:worker_id>/', views.worker_profile, name='profile'),
    path('book-worker/<int:worker_id>/', views.book_worker, name='book_worker'),
    path('worker/notifications/', views.worker_notifications, name='worker_notifications'),
    path('update_booking/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('user/notifications/', views.user_notifications, name='user_notifications'),
    path('contact/<int:booking_id>/', views.contact_page, name='contact_page'),
    path('worker/<int:worker_id>/', views.worker_profile, name='profile'),
    path('workerprofile/<int:worker_id>/', views.worker_profiles, name='worker_profiles'),
    path('submit-rating/<int:booking_id>/', views.submit_rating, name='submit_rating'),
    path('worker/bookings/', views.worker_bookings, name='worker_bookings'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('user-profile/', views.user_profile, name='user_profile'),
    path('report-userw/', views.submit_reportw, name='submit_reportw'),
    path('report-user/', views.submit_report, name='submit_report'),
    path("my-bookings/", views.user_booking, name="user_booking"),
    path('payment/<int:booking_id>/', views.payment_qr, name='payment_qr'),
    path('submit-transaction/<int:booking_id>/', views.submit_transaction, name='submit_transaction'),
    path('verify-otp/<int:booking_id>/', views.verify_otp, name='verify_otp'),
    path('verify-otp-site/<int:visit_id>/', views.verify_otp_site, name='verify_otp_site'),
    path('sitevisit/<int:worker_id>/', views.request_site_visit, name='request_site_visit'),
    path('handle-notification/<int:site_visit_id>/', views.handle_notification, name='handle_notification'),
    path('update_site_visit/<int:visit_id>/', views.update_site_visit_status,name='update_site_visit_status'),
    path('update_booking/<int:booking_id>/', views.update_booking_status, name='update_booking'),
    path('site-visit-payment/<int:visit_id>/', views.site_visit_payment_qr, name='site_visit_payment_qr'),
    path('submit-site-visit-transaction/<int:visit_id>/', views.submit_site_visit_transaction,name='submit_site_visit_transaction'),
    path('site-visit-payment-success/<int:visit_id>/', views.site_visit_payment_success,name='site_visit_payment_success'),
    path('add-bank-details/', views.add_bank_details, name='add_bank_details'),
    path('wallet/', views.worker_wallet, name='worker_wallet'),
    path('withdraw-request/', views.withdraw_request, name='withdraw_request'),
    path('sitevisit/contact/<int:visit_id>/', views.sitevisit_contact, name='sitevisit_contact'),


]