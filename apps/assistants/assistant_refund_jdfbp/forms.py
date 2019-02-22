# -*- coding: utf-8 -*-
# @Time    : 2018/12/6 15:06
# @Author  : Hann
# @Site    : 
# @File    : forms.py.py
# @Software: PyCharm


from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()