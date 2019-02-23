# -*- coding: utf-8 -*-
# @Time    : 2018/12/6 15:06
# @Author  : Hann
# @Site    : 
# @File    : forms.py.py
# @Software: PyCharm


from django import forms


class ToCustomerNum(forms.Form):
    num = forms.IntegerField(max_value=10000, min_value=1)


class UploadFileForm(forms.Form):
    file = forms.FileField()