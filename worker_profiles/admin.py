from worker_acc.models import  Workers
from django.contrib import admin
from .models import Booking, Payment
from random import randint
from .models import SiteVisitRequest
from .models import SiteVisitPayment, WorkerBankDetail, WorkerWithdrawRequest, WorkerWallet, WorkerTransactionHistory

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'worker', 'start_date', 'end_date', 'status',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('user_first_name', 'user_last_name', 'worker_full_name', 'status')

    def save_model(self, request, obj, form, change):
        if obj.booking_confirmed and not obj.verification_code:
            obj.verification_code = str(random.randint(100000, 999999))
        super().save_model(request, obj, form, change)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'worker_id', 'worker_name', 'user_id', 'user_name',
        'booking', 'payment_status', 'payment_done',
        'upi_transaction_id', 'amount', 'work_done' ,'admin_approved'
    )
    list_editable = ('payment_status', 'payment_done','admin_approved')
    list_filter = ('payment_status', 'payment_done')
    search_fields = (
        'booking_userfirst_name', 'bookinguser_last_name',
        'booking_worker_full_name', 'upi_transaction_id'
    )

    fieldsets = (
        (None, {
            'fields': ('booking', 'amount', 'upi_transaction_id', 'payment_status', 'payment_done')
        }),
    )

    def worker_id(self, obj):
        return obj.booking.worker.id
    worker_id.short_description = 'Worker ID'

    def worker_name(self, obj):
        return obj.booking.worker.full_name
    worker_name.short_description = 'Worker Name'

    def user_id(self, obj):
        return obj.booking.user.id
    user_id.short_description = 'User ID'

    def user_name(self, obj):
        return f"{obj.booking.user.first_name} {obj.booking.user.last_name}"
    user_name.short_description = 'User Name'

    def work_done(self, obj):
        return obj.booking.worker_marked_completed
    work_done.boolean = True
    work_done.short_description = 'Work Completed'

@admin.register(SiteVisitRequest)
class SiteVisitRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'worker', 'location', 'preferred_date1', 'preferred_date2', 'preferred_date3', 'submitted_at')
    search_fields = ('user_username', 'worker_full_name', 'location')
    list_filter = ('submitted_at', 'location')
@admin.register(SiteVisitPayment)
class SiteVisitPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'worker_id', 'worker_name', 'user_id', 'user_name',
        'site_visit', 'payment_status', 'payment_done', 'admin_approved',
        'upi_transaction_id', 'amount', 'site_visit_status'
    )
    list_editable = ('payment_status', 'payment_done', 'admin_approved')
    list_filter = ('payment_status', 'payment_done')
    search_fields = (
        'site_visit_userfirst_name', 'site_visituser_last_name',
        'site_visit_worker_full_name', 'upi_transaction_id'
    )

    fieldsets = (
        (None, {
            'fields': ('site_visit', 'amount', 'upi_transaction_id', 'payment_status', 'payment_done', 'admin_approved')
        }),
    )

    def worker_id(self, obj):
        return obj.site_visit.worker.id
    def worker_name(self, obj):
        return obj.site_visit.worker.full_name
    def user_id(self, obj):
        return obj.site_visit.user.id
    def user_name(self, obj):
        return f"{obj.site_visit.user.first_name} {obj.site_visit.user.last_name}"
    def site_visit_status(self, obj):
        return obj.site_visit.status

    worker_id.short_description = 'Worker ID'
    worker_name.short_description = 'Worker Name'
    user_id.short_description = 'User ID'
    user_name.short_description = 'User Name'
    site_visit_status.short_description = 'Site Visit Status'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.payment_done and obj.admin_approved:
            site_visit = obj.site_visit
            if site_visit.status != 'Accepted':
                site_visit.status = 'Accepted'
                site_visit.save()

@admin.register(WorkerBankDetail)
class WorkerBankDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'worker', 'full_name', 'account_number', 'ifsc_code', 'created_at')
    search_fields = ('worker_first_name', 'workerlast_name', 'worker_id', 'account_number')


@admin.register(WorkerWithdrawRequest)
class WorkerWithdrawRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'worker', 'bank_detail_id', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('worker_first_name', 'worker_last_name')
    list_editable = ('status',)

    def bank_detail_id(self, obj):
        try:
            return WorkerBankDetail.objects.get(worker=obj.worker).id
        except WorkerBankDetail.DoesNotExist:
            return "No Bank Details"
    bank_detail_id.short_description = 'Bank Detail ID'

    def save_model(self, request, obj, form, change):
        if obj.pk:
            old_obj = WorkerWithdrawRequest.objects.get(pk=obj.pk)
            if old_obj.status != obj.status and obj.status == 'approved':
                wallet = WorkerWallet.objects.get(worker=obj.worker)
                if wallet.available_balance >= obj.amount:
                    wallet.available_balance -= obj.amount
                    wallet.save()


                    WorkerTransactionHistory.objects.create(
                        worker=obj.worker,
                        transaction_type='withdrawal',
                        amount=obj.amount,
                        description="Withdrawal approved"
                    )
                else:
                    raise ValueError("Insufficient balance in wallet.")
        super().save_model(request, obj, form, change)