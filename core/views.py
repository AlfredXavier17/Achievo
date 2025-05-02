from django.shortcuts import render, redirect, get_object_or_404
from .forms import GoalForm, JournalEntryForm
from .models import Goal, JournalEntry, PromptTemplate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db import transaction, IntegrityError

DEFAULT_TEMPLATE = {
    "title": "Daily Reflection",
    "content": "WHAT DID I DO TODAY THAT MOVED ME CLOSER TO MY GOAL?\nWHAT OBSTACLES OR CHALLENGES DID I FACE TODAY?\nWHAT WILL I DO DIFFERENTLY OR IMPROVE TOMORROW?"
}

# GOALS + JOURNALS

@login_required
def home(request):
    goals = Goal.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home.html', {'goals': goals})

@login_required
def create_goal(request):
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('home')
    else:
        form = GoalForm()
    return render(request, 'create_goal.html', {'form': form})

@login_required
def goal_detail(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    journals = JournalEntry.objects.filter(goal=goal).order_by('-created_at')
    return render(request, 'goal_detail.html', {'goal': goal, 'journals': journals})

@login_required
def add_journal_entry(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)

    if request.method == 'POST':
        print("✅ FORM SUBMIT DETECTED")
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            journal = form.save(commit=False)
            journal.goal = goal
            journal.user = request.user
            journal.save()
            return redirect('goal_detail', goal_id=goal.id)
    else:
        form = JournalEntryForm()

    templates = PromptTemplate.objects.filter(user=request.user)
    return render(request, 'add_journal.html', {
        'form': form,
        'goal': goal,
        'templates': templates,
        'default_template': DEFAULT_TEMPLATE
    })

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
    return redirect('journal_detail', journal_id=journal.id)

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
@login_required
def autosave_goal(request, goal_id):
    if request.method == 'POST':
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        try:
            data = json.loads(request.body)
            goal.title = data.get('title', goal.title)
            goal.description = data.get('description', goal.description)
            goal.save()
            return JsonResponse({'status': 'saved'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        goal.delete()
        return redirect('home')
    return redirect('goal_detail', goal_id=goal_id)

# AUTH + LANDING

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# TEMPLATES (PROMPTS)

@login_required
def create_prompt_template(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        # Truncate title to fit max_length=100 as defined in the model
        if len(title) > 100:
            title = title[:100]
            print(f"Title truncated to 100 characters: {title}")

        PromptTemplate.objects.create(
            title=title,
            content=content,
            user=request.user
        )
        return redirect('home')

    return render(request, 'prompts/create_template.html')

@login_required
def get_template_content(request, template_id):
    try:
        template = PromptTemplate.objects.get(id=template_id, user=request.user)
        return JsonResponse({'content': template.content})
    except PromptTemplate.DoesNotExist:
        return JsonResponse({'error': 'Template not found'}, status=404)

@login_required
def edit_prompt_template(request, template_id):
    template = get_object_or_404(PromptTemplate, id=template_id, user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        if len(title) > 100:
            title = title[:100]
            print(f"Title truncated to 100 characters: {title}")

        template.title = title
        template.content = content
        template.save()
        return redirect('home')  # Change this to 'home'

    return render(request, 'prompts/edit_template.html', {'template': template})


@login_required
@transaction.atomic
def delete_prompt_template(request, template_id):
    print(f"Request method: {request.method}")
    print(f"Attempting to delete template with ID: {template_id}")
    template = get_object_or_404(PromptTemplate, id=template_id, user=request.user)
    print(f"Template found: {template.title}")
    print(f"Template title length: {len(template.title)}")
    print(f"Template user: {template.user.username}")
    goal_id = request.GET.get('goal_id', 1)  # Get goal_id from query parameter, default to 1

    if request.method == 'POST':
        try:
            template.delete()
            print(f"Template {template.title} deleted successfully")
            # Verify deletion
            exists = PromptTemplate.objects.filter(id=template_id, user=request.user).exists()
            print(f"Template still exists after deletion: {exists}")
        except IntegrityError as e:
            print(f"IntegrityError during deletion: {str(e)}")
        except Exception as e:
            print(f"Error deleting template: {str(e)}")
        return redirect('add_journal', goal_id=goal_id)

    print("Redirecting without deletion due to non-POST request")
    return redirect('add_journal', goal_id=goal_id)