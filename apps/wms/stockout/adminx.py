# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 10:18
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm


from django.core.exceptions import PermissionDenied
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext

from apps.wms.stockout.models import StockOutInfo, StockOutPenddingInfo
from apps.wms.stock.models import StockInfo


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
                        stock_order.quantity -= obj.quantity
                        try:
                            stock_order.save()
                            self.message_user("%s 出库单，出库完毕" % obj.stockout_id, 'success')
                            queryset.filter(stockout_id=obj.stockout_id).update(order_status=2)
                        except Exception as e:
                            self.message_user("%s 出库单出现错误，错误原因：%s" % (obj.stockout_id, e), 'error')
                    else:
                        self.message_user("%s 出库单出现货品错误，请查看货品是否正确" % obj.stockout_id, 'error')
                        continue

            self.message_user("成功处理 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class StockOutInfoAdmin(object):
    list_display = ["stockout_id", "source_order_id", "order_status", "category", "goods_name", "goods_id", "quantity",
                    "warehouse", "nickname", "receiver", "province", "city", "district", "mobile", "memorandum"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class StockOutPenddingInfoAdmin(object):
    list_display = ["stockout_id", "source_order_id", "order_status", "category", "goods_name", "goods_id", "quantity",
                    "warehouse", "nickname", "receiver", "province", "city", "district", "mobile", "memorandum"]

    actions = [SubmitAction, ]

    def queryset(self):
        queryset = super(StockOutPenddingInfoAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset


xadmin.site.register(StockOutPenddingInfo, StockOutPenddingInfoAdmin)
xadmin.site.register(StockOutInfo, StockOutInfoAdmin)