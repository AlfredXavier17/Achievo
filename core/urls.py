from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/',views.create_goal, name='create_goal'),
    path('goals/<int:goal_id>/', views.goal_detail, name='goal_detail'),
    path('goals/<int:goal_id>/journal/new/', views.add_journal_entry, name='add_journal'),
    path('journals/<int:journal_id>/', views.journal_detail, name='journal_detail'),
    path('journals/<int:journal_id>/delete/', views.delete_journal, name='delete_journal'),
    path('journals/<int:journal_id>/edit/', views.edit_journal, name='edit_journal'),
    path('journals/<int:journal_id>/autosave/', views.autosave_journal, name='autosave_journal'),
    path('goals/<int:goal_id>/autosave/', views.autosave_goal, name='autosave_goal'),

]
