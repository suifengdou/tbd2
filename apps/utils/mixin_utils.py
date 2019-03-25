# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 15:04
# @Author  : Hann
# @Site    : 
# @File    : mixin_utils.py
# @Software: PyCharm


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# 创建一个基础类，判断用户是否登录，如果登录则允许，未登录则转入登录界面
class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url='/users/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)