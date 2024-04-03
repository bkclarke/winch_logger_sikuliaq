# accounts/urls.py

from django.urls import include, path
from .views import SignUp
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
]