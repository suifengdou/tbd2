# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 10:18
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm
import datetime


from django.core.exceptions import PermissionDenied
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext


from apps.wms.stockin.models import StockInInfo, StockInPenddingInfo
from apps.wms.stock.models import StockInfo
from apps.base.goods.models import GoodsInfo


class SubmitAction(BaseActionView):
    action_name = "check_pporder"
    description = "审核选中的计划单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    stock_order = StockInfo.objects.filter(goods_id=obj.goods_id)
                    if stock_order:
                        stock_order = stock_order[0]
                        stock_order.quantity += obj.quantity
                        try:
                            stock_order.save()
                            self.message_user("%s 入库单，入库完毕" % obj.stockin_id, 'success')
                            queryset.filter(stockin_id=obj.stockin_id).update(order_status=2)
                        except Exception as e:
                            self.message_user("%s 入库单出现错误，错误原因：%s" % (obj.stockin_id, e), 'error')

                    else:
                        stock_order = StockInfo()
                        stock_order.goods_name = obj.goods_name
                        stock_order.goods_id = obj.goods_id
                        stock_order.goods_name = obj.goods_name
                        goods_attribute = GoodsInfo.objects.filter(goods_id=obj.goods_id)
                        if goods_attribute:
                            stock_order.category = goods_attribute[0].goods_attribute
                            stock_order.size = goods_attribute[0].size
                        else:
                            self.message_user("%s 入库单出现货品错误，请查看货品是否正确" % obj.stockin_id, 'error')
                            continue
                        stock_order.warehouse = obj.warehouse
                        stock_order.quantity = obj.quantity

                        try:
                            stock_order.save()
                            self.message_user("%s 入库单，入库完毕" % obj.stockin_id, 'success')
                            queryset.filter(stockin_id=obj.stockin_id).update(order_status=2)
                        except Exception as e:
                            self.message_user("%s 入库单出现错误，错误原因：%s" % (obj.stockin_id, e), 'error')

            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class StockInInfoAdmin(object):
    list_display = ["stockin_id", "source_order_id", "order_status", "category", "batch_num", "planorder_id", "warehouse", "goods_name", "goods_id", "quantity"]
    list_filter = ["category", "warehouse", "goods_name"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class StockInPenddingInfoAdmin(object):
    list_display = ["stockin_id", "source_order_id", "order_status", "category", "batch_num", "planorder_id", "warehouse", "goods_name", "goods_id", "quantity"]

    actions = [SubmitAction, ]

    def queryset(self):
        queryset = super(StockInPenddingInfoAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset


xadmin.site.register(StockInPenddingInfo, StockInPenddingInfoAdmin)
xadmin.site.register(StockInInfo, StockInInfoAdmin)


