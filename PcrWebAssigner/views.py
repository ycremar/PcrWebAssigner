from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User, Group

from .models import *
from .forms import *

global last_update_datetime
global next_update_datetime

def conditional_decorator(dec, condition):
    def decorator(func):
        if not condition:
            return func
        return dec(func)
    return decorator
    
def clear_all_damage_record():
    Boss.objects.all().delete()
    RealDamage.objects.all().delete()
    for player in list(User.objects.all()):
        player.profile.accumulated_damage = 0
        player.profile.total_damage_today = 0
        player.profile.acc_finishing_counts = 0
        player.profile.damage_counts = 0
        player.profile.accumulated_counts = 0
        player.profile.finishing_counts = 0
        player.save()

def do_daily_update():
    def update():
        for player in list(User.objects.all()):
            print(player.profile.total_damage_today)
            player.profile.total_damage_today = 0
            player.profile.damage_counts = 0
            player.profile.finishing_counts = 0
            player.save()
    
    current_time = datetime.utcnow()
    today_9pm = current_time.replace(hour=21, minute=0)
    yesterday_9pm = today_9pm - timedelta(days=1)
    
    try:
        last_update_datetime
    except:
        last_update_datetime = current_time
    
    if last_update_datetime < yesterday_9pm:
        update()
        last_update_datetime = current_time
        return True
        
    elif last_update_datetime < today_9pm:
        if current_time < today_9pm:
            return False
        else:
            update()
            last_update_datetime = current_time
            return True
    else:
        return False
    

@login_required(login_url='/login/')
def home(request):
    do_daily_update()
    # delete_all_damage_record()
    if Boss.objects.count() <= 0:
        for number in range(1,6):
            status = 'ongoing' if number==1 else 'future'
            # status = 'ongoing' if number==5 else 'down'
            boss = Boss.objects.create(
                epoch=1,
                number=number, 
                status=status,
                )
            # boss.damage_carried = 8537040 if number==5 else boss.maximal_hp
            boss.save()
    current_boss = Boss.objects.get(status='ongoing')
    current_epoch = current_boss.epoch
    current_perc = current_boss.current_hp/current_boss.maximal_hp
    bosses = Boss.objects.filter(epoch=current_epoch).order_by('number')
    in_battle_users = User.objects.filter(profile__in_battle=True)
    sos_users = User.objects.filter(profile__sos=True)
    current_boss_damage = RealDamage.objects.filter(boss=current_boss)
    return render(request, 'home.html', {
        'bosses': bosses,
        'battle': in_battle_users,
        'sos': sos_users,
        'epoch': current_epoch,
        'damages': current_boss_damage,
        'perc': current_perc,
    })
    
@login_required(login_url='/login/')
def simulation(request):
    return render(request, 'home.html')
    
@conditional_decorator(login_required(login_url='/login/'), not settings.DEBUG)
def real(request):
    return render(request, 'home.html')
    
@conditional_decorator(login_required(login_url='/login/'), not settings.DEBUG)
def members(request, sortby='id'):
    users = User.objects.all()
    order_by = request.GET.get('order_by', 'id')
    users = users.order_by(order_by)
    
    return render(request, 'members.html', {
        'members':users,})
        
@conditional_decorator(login_required(login_url='/login/'), not settings.DEBUG)        
def cancel_battle(request):
    player = request.user
    player.profile.in_battle = False
    player.save()
    return redirect('home')
    
def sos(request):
    player = request.user
    player.profile.sos = not player.profile.sos
    player.save()
    return redirect('damage')
        
@conditional_decorator(login_required(login_url='/login/'), not settings.DEBUG)
def report_damage(request):
    player = request.user
    boss = Boss.objects.get(status='ongoing')
    if request.method == 'POST':
        form = damage_report_form(request.POST)
        if form.is_valid() and form.cleaned_data['damage']<=boss.current_hp:
            obj = form.save(commit=False)
            obj.player = player
            obj.boss = boss
            obj.save()
            
            boss.damage_carried += obj.damage
            boss.save()
            finishing = check_finishing(boss)
            
            player.profile.total_damage_today += obj.damage
            player.profile.accumulated_damage += obj.damage
            print(player.profile.finishing)
            if finishing and not player.profile.finishing:
                player.profile.finishing_counts += 1
                player.profile.acc_finishing_counts += 1
                player.profile.finishing = True
                player.save()
            elif finishing and player.profile.finishing:
                player.profile.damage_counts += 1
                player.profile.accumulated_counts += 1
                player.profile.finishing = False
                player.save()
            elif player.profile.finishing:
                player.profile.damage_counts += 1
                player.profile.accumulated_counts += 1
                player.save()
                
            player.profile.in_battle = False
            player.save()
            messages.success(request, '伤害已记录。')
        else: 
            messages.error(request, mark_safe("{0}".format(form.errors)))
            player.profile.in_battle = False
            player.profile.sos = False
            player.save()
        return redirect('home')
    else:
        player.profile.in_battle = True
        player.save()
        form = damage_report_form()
        title = '挂树中（会长我挂树了！）' if player.profile.sos else '正在战斗'
        return render(request, 'damage.html', {
            'form': form,
            'title': title,
            'player': player,
            })
            
def check_finishing(boss):
    current_epoch = boss.epoch
    
    if boss.current_hp<=0:
        if boss.number<5:
            next_boss = Boss.objects.get(
                epoch=boss.epoch, 
                number=boss.number+1)
            boss.status = 'down'
            boss.save()
            next_boss.status = 'ongoing'
            next_boss.save()
            return True
        
        else:
            boss.status = 'down'
            boss.save()
            for number in range(1,6):
                status = 'ongoing' if number==1 else 'future'
                boss = Boss.objects.create(
                    epoch=current_epoch+1,
                    number=number, 
                    status=status)
                boss.save()
            return True
    
    else:
        return False
        
