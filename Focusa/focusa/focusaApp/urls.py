from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Define your URL patterns here
    path('', login_required(home), name='home'),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('dashboard/', login_required(dashboard), name='dashboard'),
]