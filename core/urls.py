from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_goal, name='create_goal'),
    path('goals/<int:goal_id>/', views.goal_detail, name='goal_detail'),
    path('goals/<int:goal_id>/journal/new/', views.add_journal_entry, name='add_journal'),
    path('journals/<int:journal_id>/', views.journal_detail, name='journal_detail'),
    path('journals/<int:journal_id>/delete/', views.delete_journal, name='delete_journal'),
    path('journals/<int:journal_id>/edit/', views.edit_journal, name='edit_journal'),
    path('journals/<int:journal_id>/autosave/', views.autosave_journal, name='autosave_journal'),
    path('goals/<int:goal_id>/autosave/', views.autosave_goal, name='autosave_goal'),
    path('goals/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('landing/', views.landing_page, name='landing_page'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),

    # PROMPTS (only what’s needed)
    path('prompts/new/', views.create_prompt_template, name='create_template'),
    path('prompts/<int:template_id>/json/', views.get_template_content, name='get_template_content'),
    path('prompts/<int:template_id>/edit/', views.edit_prompt_template, name='edit_prompt_template'),
    path('prompts/<int:template_id>/delete/', views.delete_prompt_template, name='delete_prompt_template'),

]