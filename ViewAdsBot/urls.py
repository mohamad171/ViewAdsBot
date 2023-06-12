from django.contrib import admin
from django.urls import path
from website.views import run_tasks

urlpatterns = [
    path('admin/', admin.site.urls),
    path('run-tasks',run_tasks)
]
