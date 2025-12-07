from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Define your URL patterns here
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('redirect-after-login/', redirect_after_login, name='redirect_after_login'),
]