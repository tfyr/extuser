import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class UserProfile(models.Model):
    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restore_code = models.IntegerField(default=None, blank=True, null=True)
    ts = models.DateTimeField(default=None, blank=True, null=True)
    cart_id = models.IntegerField('cart_id', default=None, blank=True, null=True)
    offer = models.BooleanField('Отправлять предложения', default=False, null=False, blank=False)
    email_checked = models.BooleanField('Email подтвержден', default=False, null=False, blank=False)
    phone_checked = models.BooleanField('Телефон подтвержден', default=False, null=False, blank=False)
    bdate = models.DateField('Дата рождения', default=None, blank=False, null=True)
    confirm_code_phone = models.IntegerField('Код подтверждения телефона', default=None, blank=True, null=True)
    confirm_phone = models.CharField('Подтверждаемый телефон', max_length=20, default=None, null=True, blank=True)
    confirm_code_phone_ts = models.DateTimeField('Дата и время кода подтверждения телефона', auto_now_add=True, blank=True, null=True)
    agent_id = models.IntegerField(verbose_name=u'Контрагент', default=None, null=True, blank=True)
    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class Smsconfirm(models.Model):
    class Meta:
        verbose_name = "СМС подтверждение"
        verbose_name_plural = "СМС подтверждения"
    session_key = models.CharField('сессия', max_length=128, default=None, null=True, blank=True, )
    creation = models.DateTimeField('создание', null=False, default=datetime.datetime.now, blank=False )
    phone = models.CharField('Телефон', max_length=11, default=None, null=True, blank=True, )
    smscode = models.CharField('sms код', max_length=6, default=None, null=True, blank=True, )
    checked = models.BooleanField(verbose_name="checked", null=False, blank=False, default=False)
    check_count = models.IntegerField(verbose_name="Попыток", default=0,)


class RestorePswdByEmail(models.Model):
    class Meta:
        verbose_name = "Восстановление пароля по Email"
        verbose_name_plural = "Восстановление пароля по Email"
    session_key = models.CharField('сессия', max_length=128, default=None, null=True, blank=True, )
    creation = models.DateTimeField('создание', null=False, default=datetime.datetime.now, blank=False )
    login = models.CharField('Логин', max_length=128, default=None, null=True, blank=True, )
    code = models.CharField('Код', max_length=255, default=None, null=True, blank=True, )
    checked = models.BooleanField(verbose_name="checked", null=False, blank=False, default=False)
    check_count = models.IntegerField(verbose_name="Попыток", default=0,)
