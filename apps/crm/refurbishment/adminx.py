# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 9:19
# @Author  : Hann
# @Site    : 
# @File    : adminx.py.py
# @Software: PyCharm


import xadmin

from .models import OriRefurbishInfo, ApprasialInfo, PrivateOriRefurbishInfo, RefurbishInfo, RefurbishTechSummary, PrivateRefurbishTechSummary, RefurbishGoodSummary


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
    list_filter = ['ref_time', 'goods_name', 'appraisal', 'creator', 'create_time', 'submit_tag']
    search_fields = ["tail_sn", "pre_sn", "new_sn"]
    model_icon = 'fa fa-refresh'
    ordering = ['-ref_time']
    exclude = ['creator', 'created_by']


class PrivateOriRefurbishInfoAdmin(SetUserAdminMixin, object):
    list_display = ['ref_time', 'goods_name', 'appraisal', 'pre_sn', 'mid_batch', 'tail_sn', 'submit_tag', 'creator',
                    'create_time', 'created_by', 'new_sn']
    list_filter = ['ref_time', 'goods_name', 'appraisal', 'creator', 'create_time', 'submit_tag']
    search_fields = ["tail_sn"]
    model_icon = 'fa fa-gear'
    readonly_fields = ['submit_tag']
    ordering = ['-ref_time']
    exclude = ['creator', 'created_by']

    def queryset(self):
        request = self.request
        qs = super(PrivateOriRefurbishInfoAdmin, self).queryset()
        qs = qs.filter(created_by=request.user.id)
        return qs


class RefurbishInfoAdmin(object):
    list_display = ['ref_time', 'goods_name', 'm_sn', 'appraisal', 'technician', 'memo', 'create_time']
    list_filter = ['ref_time', 'goods_name', 'appraisal', 'technician', 'create_time', 'memo']
    search_fields = ['m_sn']
    model_icon = 'fa fa-table'
    readonly_fields = ['ref_time', 'goods_name', 'appraisal', 'technician', 'submit_tag']
    ordering = ['-ref_time']
    exclude =['creator']


class RefurbishTechSummaryAdmin(object):
    list_display = ["statistical_time", "technician", "quantity"]
    search_fields = ['technician']
    list_filter = ["statistical_time", 'technician']
    model_icon = 'fa fa-trophy'
    ordering = ['-statistical_time']


class PrivateRefurbishTechSummaryAdmin(object):
    list_display = ["statistical_time", "technician", "quantity"]
    list_filter = ["statistical_time"]
    model_icon = 'fa fa-trophy'
    ordering = ['-statistical_time']

    def queryset(self):
        request = self.request
        qs = super(PrivateRefurbishTechSummaryAdmin, self).queryset()
        qs = qs.filter(technician=request.user.username)
        return qs


class AppraisalInfoAdmin(object):
    list_display = ['appraisal', 'creator', 'create_time']
    search_feilds = ['appraisal']
    list_filter = ['appraisal']
    model_icon = 'fa fa-tags'


xadmin.site.register(OriRefurbishInfo, OriRefurbishAdmin)
xadmin.site.register(PrivateOriRefurbishInfo, PrivateOriRefurbishInfoAdmin)
xadmin.site.register(PrivateRefurbishTechSummary, PrivateRefurbishTechSummaryAdmin)
xadmin.site.register(RefurbishTechSummary, RefurbishTechSummaryAdmin)
xadmin.site.register(RefurbishInfo, RefurbishInfoAdmin)
xadmin.site.register(ApprasialInfo, AppraisalInfoAdmin)
