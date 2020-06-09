from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MaxValueValidator, MinValueValidator
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_damage_today = models.BigIntegerField(verbose_name='Total Damage Today', default=0)
    accumulated_damage = models.BigIntegerField(verbose_name='Accumulated Damage', default=0)
    damage_counts = models.SmallIntegerField(blank = False, default=0, verbose_name='Damage Counts')
    accumulated_counts = models.SmallIntegerField(blank = False, default=0, verbose_name='Accumulated Counts')
    
    finishing_counts = models.SmallIntegerField(blank = False, default=0, verbose_name='今日尾刀次数')
    acc_finishing_counts = models.SmallIntegerField(blank = False, default=0, verbose_name='总计尾刀次数')
    # Status
    in_battle = models.BooleanField(default=False, verbose_name='挑战中')
    sos = models.BooleanField(default=False, verbose_name='挂树')
    finishing = models.BooleanField(default=False, verbose_name='尾刀')
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
class Boss(models.Model):
    STATUS_opt = [('down', '已击破 Down'),
                  ('ongoing', '正在挑战 Ongoing'),
                  ('future', '待挑战 Future')]
    STATUS_dict = {k:v for k,v in STATUS_opt}
    BOSS_HP = {1:6000000, 2:8000000, 3:10000000, 4:12000000, 5:20000000}
    BOSS_NAME = {1:'一王', 2:'二王', 3:'三王', 4:'四王', 5:'五王'}
    
    epoch = models.SmallIntegerField(blank = False, default=1, verbose_name='Epoch',\
        validators=[MaxValueValidator(128), MinValueValidator(1)])
    number = models.SmallIntegerField(blank = False, default=1, verbose_name='Number',\
        validators=[MaxValueValidator(5), MinValueValidator(1)])
    damage_carried = models.BigIntegerField(default=0, verbose_name='已受到的伤害总量')
    status = models.CharField(max_length=64, default='future', choices=STATUS_opt, verbose_name='Boss当前状态')
    
    @property
    def is_active(self):
        return self.status=='ongoing'
        
    @property
    def maximal_hp(self):
        return self.BOSS_HP[self.number]
        
    @property
    def current_hp(self):
        return self.maximal_hp - self.damage_carried
        
    @property
    def get_boss_name(self):
        return self.BOSS_NAME[self.number]
        
    @property
    def get_boss_status(self):
        return self.STATUS_dict[self.status]
    
class RealDamage(models.Model):
    bonus = models.BooleanField(verbose_name='尾刀', default=False)
    damage = models.IntegerField(validators=[MinValueValidator(0)], verbose_name='当前刀伤害')
    player = models.ForeignKey(User, related_name='player_rd', on_delete=models.CASCADE)
    boss = models.ForeignKey(Boss, related_name='boss_rd', on_delete=models.CASCADE)
    notes = models.CharField(max_length=511, blank=True, verbose_name='备注（e.g. 阵容）')
    report_time = models.DateTimeField(auto_now_add=True, verbose_name='Report Time')
    class Meta:
        verbose_name = 'RealDamage'
    
class SimulatedDamage(models.Model):
    damage = models.IntegerField()
    player = models.ForeignKey(User, related_name='player_sd', on_delete=models.CASCADE)
    team_id = models.IntegerField(choices=[(1, 'Team 1'), (2, 'Team 2'), (3, 'Team 3')])
    boss = models.ForeignKey(Boss, related_name='boss_sd', on_delete=models.CASCADE)
    notes = models.CharField(max_length=511, blank=True, verbose_name='备注（e.g. 阵容）')
