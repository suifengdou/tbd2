# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    : 
# @File    : urls.py.py
# @Software: PyCharm

from django.conf.urls import url


from apps.users.views import LoginView, LogoutView

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    # url(r'^profile/$', UserInfoView.as_view(), name='profile'),
]