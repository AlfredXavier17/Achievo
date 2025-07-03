from django.contrib import admin
from django.urls import path, include 
from django.contrib.auth import views as auth_views
from core.forms import LoginForm  # ✅ Add this

urlpatterns = [
    path('', include('core.urls')),
]
