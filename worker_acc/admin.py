from django.contrib import admin
from django.utils.html import format_html
from .models import Workers, Rating
from .models import InterviewRequest

@admin.register(Workers)
class WorkersAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'age', 'mobile', 'job_category', 'experience',
        'daily_wage', 'is_approved', 'view_aadhar', 'view_proof'
    )
    list_filter = ('is_approved', 'job_category', 'state')
    search_fields = ('full_name', 'email', 'mobile', 'district')
    list_editable = ('is_approved',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('full_name', 'username', 'email', 'mobile', 'age', 'gender', 'profile_image')
        }),
        ('Job Details', {
            'fields': ('job_category', 'experience', 'working_hours', 'daily_wage')
        }),
        ('Location', {
            'fields': ('state', 'district')
        }),
        ('Documents', {
            'fields': ('aadhar', 'proof', 'view_aadhar', 'view_proof')
        }),
        ('Approval', {
            'fields': ('is_approved',)
        }),
    )

    readonly_fields = ('view_aadhar', 'view_proof', 'profile_image')

    def view_aadhar(self, obj):
        if obj.aadhar:
            return format_html('<a href="{}" target="_blank">View Aadhar</a>', obj.aadhar.url)
        return "No File"
    view_aadhar.short_description = 'Aadhar File'

    def view_proof(self, obj):
        if obj.proof:
            return format_html('<a href="{}" target="_blank">View Proof</a>', obj.proof.url)
        return "No File"
    view_proof.short_description = 'Proof File'


@admin.register(InterviewRequest)
class InterviewRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'job_role', 'phone', 'district', 'state', 'status', 'applied_at')
    list_editable = ('status',)
    list_filter = ('job_role', 'district', 'state', 'status')
    search_fields = ('full_name', 'phone', 'district', 'state')
    ordering = ('-applied_at',)