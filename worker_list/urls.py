from django.urls import path
from .views import workers_by_category
from .import views

app_name = "worker_list"


urlpatterns = [

    path('<str:job_category>/', workers_by_category, name='workers_by_category'),


]