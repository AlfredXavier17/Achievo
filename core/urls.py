from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views
from .forms import CustomPasswordResetForm
from .views import verify_email
from .views import verify_email_view


from .views import (
    AchievoPasswordResetView,
    AchievoPasswordResetDoneView,
    AchievoPasswordResetConfirmView,
    AchievoPasswordResetCompleteView,
    login_view,
    register_view
)

urlpatterns = [
    path('', views.landing_page, name='landing_page'),  
    path('home/', views.home, name='home'),       
    path('create/', views.create_goal, name='create_goal'),
    path('goals/<int:goal_id>/', views.goal_detail, name='goal_detail'),
    path('goals/<int:goal_id>/journal/new/', views.add_journal_entry, name='add_journal'),
    path('journals/<int:journal_id>/', views.journal_detail, name='journal_detail'),
    path('journals/<int:journal_id>/delete/', views.delete_journal, name='delete_journal'),
    path('journals/<int:journal_id>/edit/', views.edit_journal, name='edit_journal'),
    path('journals/<int:journal_id>/autosave/', views.autosave_journal, name='autosave_journal'),
    path('goals/<int:goal_id>/autosave/', views.autosave_goal, name='autosave_goal'),
    path('goals/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),

    # AUTH
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # PROMPTS
    path('prompts/new/', views.create_prompt_template, name='create_template'),
    path('prompts/<int:template_id>/json/', views.get_template_content, name='get_template_content'),
    path('prompts/<int:template_id>/edit/', views.edit_prompt_template, name='edit_prompt_template'),
    path('prompts/<int:template_id>/delete/', views.delete_prompt_template, name='delete_prompt_template'),

    # PASSWORD RESET
    path('password_reset/', AchievoPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', AchievoPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', AchievoPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', AchievoPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # PRIVACY
    path('privacy-policy/', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path('verify-email/<uidb64>/<token>/', verify_email_view, name='verify_email'),
    path('terms/', views.terms, name='terms'),

]
