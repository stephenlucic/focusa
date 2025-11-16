from django.urls import path
from .views import *

urlpatterns = [
    # Define your URL patterns here
    path('', home, name='home'),
]