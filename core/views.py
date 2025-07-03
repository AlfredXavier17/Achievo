from django.shortcuts import render, redirect, get_object_or_404
from .forms import GoalForm, JournalEntryForm, CustomUserCreationForm, LoginForm
from .models import Goal, JournalEntry, PromptTemplate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login, authenticate
from django.db import transaction, IntegrityError
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.contrib.auth import login
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import redirect,render
from .tokens import email_verification_token
from .models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.tokens import default_token_generator
from .tokens import email_verification_token
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
User = get_user_model()



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
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
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

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if not user.is_email_verified:
                messages.error(request, "Please verify your email before logging in.")
                return render(request, 'registration/login.html', {'form': form})

            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'registration/login.html', {'form': form})

    form = LoginForm(request=request)
    return render(request, 'registration/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.email = user.email.lower().strip()
                    user.is_active = False  # ⛔️ Make sure user is inactive until verified
                    user.save()

                    # ✅ Send verification email with uidb64
                    from .tokens import email_verification_token
                    from .utils import send_verification_email

                    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                    token = email_verification_token.make_token(user)
                    domain = request.get_host()
                    send_verification_email(user, uidb64, token, domain)

                    # 🚫 Do not auto-login
                    return render(request, 'registration/email_verification_sent.html', {'email': user.email})
            except IntegrityError:
                form.add_error('email', 'This email is already registered.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# TEMPLATES (PROMPTS)

@login_required
def create_prompt_template(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')[:100]  # Truncate to 100 chars
        content = request.POST.get('content', '')

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
        title = request.POST.get('title', '')[:100]  # Truncate to 100 chars
        content = request.POST.get('content', '')

        template.title = title
        template.content = content
        template.save()
        return redirect('home')

    return render(request, 'prompts/edit_template.html', {'template': template})

@login_required
@transaction.atomic
def delete_prompt_template(request, template_id):
    template = get_object_or_404(PromptTemplate, id=template_id, user=request.user)
    goal_id = request.GET.get('goal_id', 1)

    if request.method == 'POST':
        template.delete()
        return redirect('add_journal', goal_id=goal_id)
    return redirect('add_journal', goal_id=goal_id)

# PASSWORD RESET VIEWS

class AchievoPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = '/password_reset/done/'

class AchievoPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class AchievoPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = '/reset/done/'

class AchievoPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        login(request, user)
        messages.success(request, "Your email has been verified! 🎉")
        return redirect('home')
    else:
        messages.error(request, "Invalid or expired verification link.")
        return redirect('landing_page')
    

def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if email_verification_token.check_token(user, token):
            user.is_email_verified = True
            user.is_active = True
            user.save()
            auth_login(request, user)
            return render(request, 'registration/email_verified.html')
        else:
            return render(request, 'registration/email_invalid.html')

    except User.DoesNotExist:
        return render(request, 'registration/email_invalid.html')

def terms(request):
    return render(request, 'terms.html')
