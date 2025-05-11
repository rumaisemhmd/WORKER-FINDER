from django.db import models
from user_acc.models import Users
from django.apps import apps


class Workers(models.Model):
    ...
    is_approved = models.BooleanField(default=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    job_category = models.CharField(max_length=50)
    experience = models.IntegerField()
    working_hours = models.IntegerField()
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2)
    state = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10)
    profile_image = models.ImageField(upload_to='worker_images/', blank=True, null=True)
    rating = models.FloatField(default=0.0)  # Average rating
    aadhar = models.FileField(upload_to='uploads/aadhar/', blank=True, null=True)
    proof = models.FileField(upload_to='uploads/proof/', blank=True, null=True)

    def update_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            avg_rating = sum(r.rating_value for r in ratings) / ratings.count()
            self.rating = round(avg_rating, 2)
        else:
            self.rating = 0.0
        self.save()

    def __str__(self):
        return self.full_name



class Rating(models.Model):
    worker = models.ForeignKey('worker_acc.Workers', related_name="ratings", on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    booking = models.ForeignKey('worker_profiles.Booking', on_delete=models.CASCADE)
    rating_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'booking')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.worker.update_rating()

    def __str__(self):
        return f"{self.user.email} → {self.worker.full_name} ({self.rating_value})"

class InterviewRequest(models.Model):
    GENDER_CHOICES = (('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other'))

    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    job_role = models.CharField(max_length=100)
    experience = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name