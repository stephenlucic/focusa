from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Define your URL patterns here
    path('', login_required(kanban), name='kanban'),
]