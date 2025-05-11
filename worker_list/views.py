from worker_acc.models import Workers
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import WorkerReport, Workers
from user_acc.models import Users
from django.contrib import messages

def workers_by_category(request, job_category):
    workers = Workers.objects.filter(job_category__iexact=job_category)

    context = {
        'job_category': job_category.capitalize(),
        'workers': workers
    }

    return render(request, 'worker_list/workers_by_category.html', context)



