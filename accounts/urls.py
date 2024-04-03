# accounts/urls.py

from django.urls import include, path
from .views import SignUp
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(), {'template_name': 'registration/login.html'}, name = 'login'),
    path('logout/', auth_views.LogoutView.as_view(), {'template_name': 'registration/logged_out.html'}, name = 'logout')
]