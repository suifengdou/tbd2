# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 9:19
# @Author  : Hann
# @Site    :
# @File    : adminx.py.py
# @Software: PyCharm


import xadmin

from .models import OriorderInfo, ErrorOrderInfo, AppointmentOrderInfo


class SetUserAdminMixin(object):
    def save_models(self):
        obj = self.new_obj
        request = self.request
        if obj.created_by_id is None:
            obj.created_by_id = request.user.id
            obj.creator = request.user.username
            obj.save()
        super().save_models()


class OriorderInfoAdmin(SetUserAdminMixin, object):
    list_display = ['order_id', 'nickname', 'total_amount', 'payment_amount', 'order_status', 'payment_time', 'goods_title',
                    'goods_quantity', 'shop_name', 'refund_amount','create_time', 'created_by']
    list_filter = ['payment_time', 'order_status', 'created_by']
    search_fields = ["order_id", "nickname"]
    # model_icon = 'fa fa-refresh'
    ordering = ['payment_time']
    exclude = ['creator']


xadmin.site.register(OriorderInfo, OriorderInfoAdmin)