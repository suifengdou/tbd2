# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 9:19
# @Author  : Hann
# @Site    :
# @File    : views.py
# @Software: PyCharm

from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http import HttpResponse, StreamingHttpResponse
# from .forms import UploadFileForm
from django.db.models import Q
from django.utils.six import moves
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd



from apps.crm.customers.models import CustomerInfo, CustomerTendency
from .models import OriRefurbishInfo, RefurbishInfo, ApprasialInfo

from apps.utils.mixin_utils import LoginRequiredMixin


class RefurbishTask(LoginRequiredMixin, View):

    def get(self, request):
        elements = {"pending_num": 0, "total_num": 0}



        return render(request, 'crm/refurbishment/upload.html', {
            "index_tag": "crm_refurbishment_task",
        })


class RefurbishOverView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'crm/refurbishment/overview.html', {
            "index_tag": "crm_refurbishment_overview",
        })