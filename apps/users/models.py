# -*- coding:utf-8 -*-

from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


from db.base_model import BaseModel
from apps.base.company.models import CompanyInfo


# Create your models here.
class UserProfile(AbstractUser, BaseModel):
    STATUS = (
        (0, '非管理'),
        (1, '管理'),
    )
    PLATFORM = (
        (0, '无'),
        (1, '淘系'),
        (2, '京东'),
        (3, '官方商城'),
        (4, '售后'),
    )
    nick = models.CharField(max_length=50, verbose_name=u'昵称', default=u'')
    platform = models.SmallIntegerField(choices=PLATFORM, default=0, verbose_name='平台')
    company = models.ForeignKey(CompanyInfo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属公司')

    class Meta:
        verbose_name = u'USR-用户信息'
        verbose_name_plural = verbose_name
        db_table = 'usr_userprofile'

    def __str__(self):
        return self.username


class EmailVerifyRecord(models.Model):
    code = models.CharField(max_length=20, verbose_name=u'验证码')
    email = models.EmailField(max_length=50, verbose_name=u'邮箱')
    send_type = models.CharField(choices=(("register", u"注册"), ('forget', u'找回密码'), ('update_email', u'修改邮箱')), max_length=20, verbose_name=u'验证码类型')
    send_time = models.DateTimeField(default=datetime.now, verbose_name=u'发送时间')

    class Meta:
        verbose_name = u'USR-邮箱验证码'
        verbose_name_plural = verbose_name
        db_table = 'usr_emailverifyrecord'

    def __str__(self):
        return '{0}({1})'.format(self.code, self.email)