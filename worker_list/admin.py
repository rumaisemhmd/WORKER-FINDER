from django.contrib import admin
from .models import WorkerReport
from .models import UserReport

@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'user', 'reason','description','date_reported')
    list_filter = ('reason', 'date_reported')
    search_fields = ('reporter_full_name', 'reason', 'description', 'reason')
    readonly_fields = ('date_reported',)
    ordering = ('-date_reported',)

@admin.register(WorkerReport)
class WorkerReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'worker', 'reason','description','date_reported')
    list_filter = ('reason', 'date_reported')
    search_fields = ('reporter_full_name', 'reason', 'description', 'reason')
    readonly_fields = ('date_reported',)
    ordering = ('-date_reported',)

