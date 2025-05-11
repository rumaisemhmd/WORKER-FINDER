from user_acc.models import Users
from worker_acc.models import Workers
from django.db import models

class WorkerReport(models.Model):
    reporter = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='reports_made')
    worker = models.ForeignKey(Workers, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.CharField(max_length=255)
    description = models.TextField()
    date_reported = models.DateTimeField(auto_now_add=True)

    def reporter_mobile(self):
        return self.reporter.mobile
    reporter_mobile.short_description = 'Reporter Mobile'

class UserReport(models.Model):
    reporter = models.ForeignKey(Workers, on_delete=models.CASCADE, related_name='user_reports_made')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='user_reports_received')
    reason = models.CharField(max_length=255)
    description = models.TextField()
    date_reported = models.DateTimeField(auto_now_add=True)