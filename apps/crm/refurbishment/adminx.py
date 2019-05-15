# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 9:19
# @Author  : Hann
# @Site    : 
# @File    : adminx.py.py
# @Software: PyCharm


import xadmin

from .models import OriRefurbishInfo, ApprasialInfo, PrivateOriRefurbishInfo


class SetUserAdminMixin(object):
    def save_models(self):
        obj = self.new_obj
        request = self.request
        if obj.created_by_id is None:
            obj.created_by_id = request.user.id
            obj.creator = request.user.username
            obj.save()
        super().save_models()


class OriRefurbishAdmin(SetUserAdminMixin, object):
    list_display = ['ref_time', 'goods_name', 'appraisal', 'pre_sn', 'mid_batch', 'tail_sn', 'submit_tag', 'creator',
                    'create_time', 'created_by', 'new_sn']
    list_filter = ['ref_time', 'goods_name', 'appraisal', 'creator', 'create_time']
    model_icon = 'fa fa-refresh'
    readonly_fields = ['submit_tag']
    exclude = ['creator', 'created_by']


class PrivateOriRefurbishInfoAdmin(SetUserAdminMixin, object):
    list_display = ['ref_time', 'goods_name', 'appraisal', 'pre_sn', 'mid_batch', 'tail_sn', 'submit_tag', 'creator',
                    'create_time', 'created_by', 'new_sn']
    list_filter = ['ref_time', 'goods_name', 'appraisal', 'creator', 'create_time']
    model_icon = 'fa fa-refresh'
    readonly_fields = ['submit_tag']
    exclude = ['creator', 'created_by']

    def queryset(self):
        request = self.request
        qs = super(PrivateOriRefurbishInfoAdmin, self).queryset()
        qs = qs.filter(created_by=request.user.id)
        return qs


class AppraisalInfoAdmin(object):
    list_display = ['appraisal', 'creator', 'create_time']
    search_feilds = ['appraisal']
    list_filter = ['appraisal']


xadmin.site.register(OriRefurbishInfo, OriRefurbishAdmin)
xadmin.site.register(PrivateOriRefurbishInfo, PrivateOriRefurbishInfoAdmin)
xadmin.site.register(ApprasialInfo, AppraisalInfoAdmin)
