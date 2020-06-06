from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User, Group

from .forms import SignUpForm, AdminChangePasswordForm, ChangePasswordForm

@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    return render(request, 'manage_users.html')

@login_required(login_url='/login/')
def manage_my_account(request):
    return render(request, 'manage_my_account.html')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            # group = form.cleaned_data.get('group')
            user = authenticate(username=username, password=raw_password)
            # group.user_set.add(user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def all_users(request):
    users = User.objects.all()
    return render(request, 'user_list.html', { 'users': users })
    
@user_passes_test(lambda u: u.is_superuser)
def change_users_pwd(request, id):
    user = User.objects.get(id = id)
    if request.user.id == id:
        return redirect('change_my_pwd')
    if request.method == 'POST':
        form = AdminChangePasswordForm(user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Your password is successfully updated!")
            return redirect('user_list')
    else:
        form = AdminChangePasswordForm(user)
    return render(request, 'change_pwd.html', {'form': form, 'username': user.username})

@login_required(login_url='/login/')
def change_my_pwd(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Your password is successfully updated!")
            return redirect('account')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'change_my_pwd.html', {
        'form': form
    })
