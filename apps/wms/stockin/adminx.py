# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 10:18
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm


import datetime
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext


from django.core.exceptions import PermissionDenied
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse

from django.contrib.admin.utils import get_deleted_objects

from apps.oms.qcorder.models import QCInfo
from apps.wms.stockin.models import StockInInfo, StockInPenddingInfo
from apps.wms.stock.models import StockInfo
from apps.base.goods.models import GoodsInfo
ACTION_CHECKBOX_NAME = '_selected_action'


class RejectSelectedQCAction(BaseActionView):

    action_name = "reject_selected"
    description = '驳回选中的入库单'

    delete_confirmation_template = None
    delete_selected_confirmation_template = None

    delete_models_batch = False

    model_perm = 'change'
    icon = 'fa fa-times'

    @filter_hook
    def reject_models(self, queryset):
        n = queryset.count()
        if n:
            for obj in queryset:
                qc_tag = QCInfo.objects.filter(qc_order_id=obj.source_order_id, order_status__in=[1, 2])
                if qc_tag.exists():
                    qc_order = qc_tag[0]
                    qc_order.order_status = 1
                    qc_order.save()
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 的入库单取消成功，QC订单已驳回到待递交界面。" % obj.source_order_id, "success")
                else:
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 的入库单不是验货入库，已经取消成功。" % obj.source_order_id, "success")
            self.message_user("成功驳回 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None

    @filter_hook
    def do_action(self, queryset):
        # Check that the user has delete permission for the actual model
        if not self.has_change_permission():
            raise PermissionDenied

        using = router.db_for_write(self.model)

        # Populate deletable_objects, a data structure of all related objects that
        # will also be deleted.
        deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
            queryset, self.opts, self.user, self.admin_site, using)

        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if self.request.POST.get('post'):
            if not self.has_change_permission():
                raise PermissionDenied
            self.reject_models(queryset)
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_text(self.opts.verbose_name)
        else:
            objects_name = force_text(self.opts.verbose_name_plural)
        perms_needed = []
        if perms_needed or protected:
            title = "Cannot reject %(name)s" % {"name": objects_name}
        else:
            title = "Are you sure?"

        context = self.get_context()
        context.update({
            "title": title,
            "objects_name": objects_name,
            "deletable_objects": [deletable_objects],
            'queryset': queryset,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": self.opts,
            "app_label": self.app_label,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        })

        # Display the confirmation page
        return TemplateResponse(self.request, self.delete_selected_confirmation_template or
                                self.get_template_list('views/model_reject_selected_confirm.html'), context)


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
                            n -= 1
                            obj.error_tag = 1
                            obj.save()

                    else:
                        stock_order = StockInfo()
                        stock_order.goods_name = obj.goods_name
                        stock_order.goods_id = obj.goods_id
                        goods_attribute = GoodsInfo.objects.filter(goods_id=obj.goods_id)
                        if goods_attribute:
                            stock_order.category = goods_attribute[0].goods_attribute
                            stock_order.size = goods_attribute[0].size
                        else:
                            self.message_user("%s 入库单出现货品错误，请查看货品是否正确" % obj.stockin_id, 'error')
                            n -= 1
                            obj.error_tag = 2
                            obj.save()
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

    actions = [SubmitAction, RejectSelectedQCAction]

    def queryset(self):
        queryset = super(StockInPenddingInfoAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset


xadmin.site.register(StockInPenddingInfo, StockInPenddingInfoAdmin)
xadmin.site.register(StockInInfo, StockInInfoAdmin)


