# -*- coding: utf-8 -*-
# @Time    : 2019/7/5 8:59
# @Author  : Hann
# @Site    : 
# @File    : adminx.py.py
# @Software: PyCharm

from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
import xadmin
from xadmin.layout import Fieldset

from .models import EditionStatement


class EditionStatementAdmin(object):
    list_display = ['version_number', 'description']

    form_layout = [
        Fieldset('必填信息',
                 'version_number', 'description'),
        Fieldset(None,
                 'creator', 'is_delete', **{"style": "display:None"}),
    ]

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.description = obj.description.replace('\r\n', '<br>')
        obj.creator = request.user.username
        obj.save()

        super().save_models()

    def results(self):
        results = []
        for obj in self.result_list:
            obj.description = mark_safe(obj.description)
            results.append(self.result_row(obj))
        return results


xadmin.site.register(EditionStatement, EditionStatementAdmin)