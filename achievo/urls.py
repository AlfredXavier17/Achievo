from django.contrib import admin
from django.urls import path, include 
from django.contrib.auth import views as auth_views
from core.forms import LoginForm  # ✅ Add this

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    
    # ✅ Use your custom login form + template
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=LoginForm
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
