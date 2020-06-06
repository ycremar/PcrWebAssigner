from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User, Group

from .models import *
from .forms import *

def conditional_decorator(dec, condition):
    def decorator(func):
        if not condition:
            return func
        return dec(func)
    return decorator


@login_required(login_url='/login/')
def home(request):
    if Boss.objects.count() <= 0:
        for number in range(1,6):
            # status = 'ongoing' if number==1 else 'future'
            status = 'ongoing' if number==5 else 'down'
            boss = Boss.objects.create(
                epoch=3,
                number=number, 
                status=status,
                )
            boss.damage_carried = 8537040 if number==5 else boss.maximal_hp
            boss.save()
    print(request.user.profile.in_battle)
    current_epoch = Boss.objects.get(status='ongoing').epoch
    bosses = Boss.objects.filter(epoch=current_epoch).order_by('number')
    in_battle_users = User.objects.filter(profile__in_battle=True)
    sos_users = User.objects.filter(profile__sos=True)
    return render(request, 'home.html', {
        'bosses': bosses,
        'battle': in_battle_users,
        'sos': sos_users,
        'epoch': current_epoch,
    })
    
@login_required(login_url='/login/')
def simulation(request):
    return render(request, 'home.html')
    
@login_required(login_url='/login/')
def real(request):
    return render(request, 'home.html')
    
@conditional_decorator(login_required(login_url='/login/'), not settings.DEBUG)
def members(request, sortby='id'):
    users = User.objects.all()
    # print(len(users), users.values('profile'))
    order_by = request.GET.get('order_by', 'id')
    users = users.order_by(order_by)
    
    return render(request, 'members.html', {
        'members':users,})
        
@conditional_decorator(login_required(login_url='/login/'), not settings.DEBUG)
def report_damage(request):
    player = request.user
    boss = Boss.objects.get(status='ongoing')
    if request.method == 'POST':
        form = damage_report_form(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.player = player
            obj.boss = boss
            obj.save()
            
            boss.damage_carried += obj.damage
            boss.save()
            
            player.profile.total_damage_today += obj.damage
            player.profile.accumulated_damage += obj.damage
            player.profile.damage_counts += 1
            player.profile.in_battle = False
            player.save()
            messages.success(request, '伤害已记录。')
        else: 
            messages.error(request, mark_safe("{0}".format(form.errors)))
            player.profile.in_battle = False
            player.save()
        return redirect('home')
    else:
        player.profile.in_battle = True
        player.save()
        form = damage_report_form()
        title = '正在战斗'
        return render(request, 'damage.html', {
            'form': form,
            'title': title,
            })
            
# @conditional_decorator(login_required(login_url='/login/'), not settings.DEBUG)
# def finish_boss(request):