"""PcrWebAssigner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from PcrWebAssigner import views

from PcrWebAssigner.registration.views import sign_up, manage_users, all_users, manage_my_account, change_my_pwd, change_users_pwd
from django.contrib.auth import views as auth_views
from PcrWebAssigner.registration.forms import AdminChangePasswordForm

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('simulation/', views.simulation, name='simulation'),
    path('damage/', views.report_damage, name='damage'),
    path('damage/sos/', views.sos, name='sos'),
    path('damage/cancel_battle/', views.cancel_battle, name='cancel_battle'),
    path('members/', views.members, name='members'),
    
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    path('account/', manage_my_account, name='account'),
    path('account/change_pwd/', change_my_pwd, name='change_my_pwd'),
    path('account/reset_pwd/', auth_views.PasswordResetView.\
        as_view(template_name='reset_pwd.html', success_url='done/', subject_template_name='reset_pwd_subject.txt',\
            email_template_name = 'reset_pwd_email.html'), name='reset_pwd'),
    path('account/reset_pwd/done/',\
        auth_views.PasswordResetDoneView.as_view(template_name='reset_pwd_done.html'), name='reset_pwd_done'),
    path('account/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.\
        as_view(template_name='reset_pwd_confirm.html', success_url='/account/reset/done/',\
        form_class=AdminChangePasswordForm), name='reset_pwd_confirm'),
    path('account/reset/done/', auth_views.PasswordResetCompleteView.\
        as_view(template_name='reset_pwd_complete.html'), name='reset_pwd_complete'),
    path('manage_users/', manage_users, name='manage_users'),
    path('manage_users/sign_up/', sign_up, name='sign_up'),
    path('manage_users/user_list/', all_users, name='user_list'),
    path('manage_users/user_list/change_pwd/<int:id>/', change_users_pwd, name='change_users_pwd'),
    path('admin/', admin.site.urls, name='admin'),
]
