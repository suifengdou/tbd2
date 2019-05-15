# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 9:28
# @Author  : Hann
# @Site    : 
# @File    : urls.py
# @Software: PyCharm


from django.conf.urls import url

from .views import RefurbishTask, RefurbishOverView

urlpatterns = [
    url(r'^upload/$', RefurbishTask.as_view(), name='upload'),
    url(r'^overview/$', RefurbishOverView.as_view(), name='overview'),
]









