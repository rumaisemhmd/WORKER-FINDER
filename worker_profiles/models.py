from django.db import models
from user_acc.models import Users
from worker_acc.models import Workers
from datetime import timedelta
import random

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    worker = models.ForeignKey(Workers, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="user_bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    worker_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contact_visible_until = models.DateField(null=True, blank=True)
    worker_notified = models.BooleanField(default=False)
    work_site = models.CharField(max_length=255, null=True, blank=True)
    estimated_days = models.IntegerField(null=True, blank=True)
    final_start_date = models.DateField(null=True, blank=True)
    final_end_date = models.DateField(null=True, blank=True)
    booking_confirmed = models.BooleanField(default=False)
    worker_marked_completed = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.booking_confirmed and not self.verification_code:
            self.verification_code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def calculate_final_end_date(self):
        if self.final_start_date and self.estimated_days:
            return self.final_start_date + timedelta(days=self.estimated_days - 1)
        return None

    def _str_(self):
        return f"Booking by {self.user.first_name} for {self.worker.full_name} from {self.start_date} to {self.end_date}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_done = models.BooleanField(default=False)
    admin_approved = models.BooleanField(default=False)
    upi_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def _str_(self):
        return f"Payment for Booking ID {self.booking.id} - Status: {self.payment_status}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.payment_done and self.admin_approved:
            booking = self.booking
            if not booking.booking_confirmed:
                booking.booking_confirmed = True
                booking.save()

class SiteVisitRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    worker = models.ForeignKey(Workers, on_delete=models.CASCADE)
    bio = models.TextField()
    preferred_date1 = models.DateField()
    preferred_date2 = models.DateField(blank=True, null=True)
    preferred_date3 = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    worker_response = models.TextField(blank=True, null=True)
    confirmed_date = models.DateField(blank=True, null=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    worker_marked_completed = models.BooleanField(default=False)

    def _str_(self):
        return f"Site Visit Request by {self.user.username} for {self.worker.full_name}"

    def save(self, *args, **kwargs):
        if self.confirmed_date and not self.verification_code:
            self.verification_code = f"{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

class SiteVisitPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    site_visit = models.OneToOneField(SiteVisitRequest, on_delete=models.CASCADE, related_name="site_visit_payment")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_done = models.BooleanField(default=False)
    admin_approved = models.BooleanField(default=False)  # <-- new field
    upi_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def _str_(self):
        return f"Payment for Site Visit ID {self.site_visit.id} - Status: {self.payment_status}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.payment_done and self.admin_approved:
            site_visit = self.site_visit
            if site_visit.status != 'Completed':
                site_visit.status = 'Completed'
                site_visit.save()


class WorkerBankDetail(models.Model):
    worker = models.OneToOneField(Workers, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.worker.first_name} {self.worker.last_name} (ID: {self.worker.id})"

class WorkerWallet(models.Model):
    worker = models.OneToOneField(Workers, on_delete=models.CASCADE)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def _str_(self):
        return f"{self.worker.first_name} Wallet"


class WorkerTransactionHistory(models.Model):
    TRANSACTION_TYPE = (
        ('earning', 'Earning'),
        ('withdrawal', 'Withdrawal'),
    )
    worker = models.ForeignKey(Workers, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def _str_(self):
        return f"{self.worker.first_name} - {self.transaction_type} - {self.amount}"

class WorkerWithdrawRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    worker = models.ForeignKey(Workers, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bank_account_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def _str_(self):
        return f"{self.worker.first_name} - {self.amount} ₹ - {self.status}"

