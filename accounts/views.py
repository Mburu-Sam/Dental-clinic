from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')

        errors = []
        if not first_name:
            errors.append('First name is required.')
        if not username:
            errors.append('Username is required.')
        if not email:
            errors.append('Email address is required for appointment confirmation and reminders.')
        if User.objects.filter(username=username).exists():
            errors.append('That username is already taken.')
        if email and User.objects.filter(email=email).exists():
            errors.append('An account with that email already exists.')
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters.')
        if password1 != password2:
            errors.append('Passwords do not match.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            user = User.objects.create_user(
                username   = username,
                email      = email,
                password   = password1,
                first_name = first_name,
                last_name  = last_name,
            )
            login(request, user)
            messages.success(request,
                f'Welcome, {first_name}! Your account has been created.')
            return redirect('book_appointment')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'book_appointment')
            messages.success(request,
                f'Welcome back, {user.first_name or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request,
                'Invalid username or password. Please try again.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')
