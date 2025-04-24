from django.shortcuts import render, redirect, get_object_or_404
from .forms import GoalForm,JournalEntryForm
from .models import Goal, JournalEntry
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@login_required
def home(request):
    goals = Goal.objects.filter(user=request.user).order_by('-created_at') 
    return render(request, 'home.html', {'goals':goals})

@login_required
def create_goal(request):
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal=form.save(commit=False)
            goal.user = request.user 
            goal.save()
            return redirect('home')
    else:
        form=GoalForm()
    return render(request,'create_goal.html',{'form':form})

@login_required
def goal_detail(request,goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    journals = JournalEntry.objects.filter(goal=goal).order_by('-created_at')
    return render(request, 'goal_detail.html',{'goal': goal, 'journals': journals})

@login_required
def add_journal_entry(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)

    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            journal = form.save(commit=False)
            journal.goal = goal
            journal.user = request.user
            journal.save()
            return redirect('goal_detail', goal_id=goal.id)
    else:
        form = JournalEntryForm()

    return render(request, 'add_journal.html', {'form': form, 'goal': goal})


@login_required
def journal_detail(request, journal_id):
    journal = get_object_or_404(JournalEntry, id=journal_id, user=request.user)
    return render(request, 'journal_detail.html', {'journal': journal})

@login_required
def delete_journal(request, journal_id):
    journal = get_object_or_404(JournalEntry, id=journal_id, user=request.user)

    if request.method == 'POST':
        goal_id = journal.goal.id
        journal.delete()
        return redirect('goal_detail', goal_id=goal_id)

    return render(request, 'delete_journal.html', {'journal': journal})

@login_required
def edit_journal(request, journal_id):
    journal = get_object_or_404(JournalEntry, id=journal_id, user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        journal.title = title if title else "New Entry"
        journal.content = content
        journal.save()
        return redirect('journal_detail', journal_id=journal.id)

    return render(request, 'journal_detail.html', {'journal': journal})


@csrf_exempt
@login_required
def autosave_journal(request, journal_id):
    if request.method == 'POST':
        journal = get_object_or_404(JournalEntry, id=journal_id, user=request.user)
        try:
            data = json.loads(request.body)
            journal.title = data.get('title', '')
            journal.content = data.get('content', '')
            journal.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
@csrf_exempt
def autosave_goal(request, goal_id):
    if request.method == 'POST' and request.user.is_authenticated:
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        data = json.loads(request.body)

        title = data.get('title')
        description = data.get('description')

        if title is not None:
            goal.title = title
        if description is not None:
            goal.description = description

        goal.save()
        return JsonResponse({'status': 'saved'})

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        goal.delete()
        return redirect('home')  # or whatever your home view is called
    return redirect('goal_detail', goal_id=goal_id)
