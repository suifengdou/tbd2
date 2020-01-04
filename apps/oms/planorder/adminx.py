# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 9:59
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm
import datetime, re


from django.core.exceptions import PermissionDenied
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse

from django.contrib.admin.utils import get_deleted_objects

import pandas as pd
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset

from .models import PlanOrderInfo, PlanOrderPenddingInfo, PlanOrderSubmitInfo

from apps.oms.manuorder.models import ManuOrderInfo
from apps.base.relationship.models import GoodsToManufactoryInfo, PartToProductInfo
from apps.oms.cusrequisition.models import CusRequisitionInfo
from apps.base.goods.models import MachineInfo, PartInfo


ACTION_CHECKBOX_NAME = '_selected_action'

# 驳回审核
class RejectSelectedAction(BaseActionView):

    action_name = "reject_selected"
    description = '驳回选中的工单'

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
                if obj.order_status == 1:
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 取消成功" % obj.planorder_id, "success")
                elif obj.order_status == 2:
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 驳回上一级成功" % obj.planorder_id, "success")
                elif obj.order_status == 3:
                    self.message_user("%s 已递交到工厂订单，驳回工厂订单，则自动驳回此计划单。" % obj.planorder_id, "success")
                    n -= 1
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


class CheckAction(BaseActionView):
    action_name = "submit_oriorder"
    description = "审核选中的计划单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = True

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
                    obj.update(order_status=2)
            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class SubmitActionPO(BaseActionView):
    action_name = "submit_oriorder"
    description = "递交选中的计划单"
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
                queryset.update(order_status=3)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    manu_order = ManuOrderInfo.objects.filter(planorder_id=obj.planorder_id, order_status__in=[1, 2, 3, 4])
                    if manu_order.exists():
                        self.message_user("此订单%s已经存在工厂订单，请不要重复递交" % obj.planorder_id, "error")
                        obj.tag_sign = 1
                        obj.save()
                        continue
                    else:

                        # 创建工厂订单
                        manufactory_order = ManuOrderInfo()
                        manufactory_order.planorder_id = obj.planorder_id
                        estimated_time = obj.estimated_time
                        pre_year_num = int(datetime.datetime.strftime(estimated_time, "%Y")[-2:]) + 17
                        pre_week_num = int(datetime.datetime.strftime(estimated_time, "%U")) + 1
                        if len(str(pre_week_num)) == 1:
                            pre_week_num = "0" + str(pre_week_num)
                        goods_number = obj.goods_name.goods_number
                        category = obj.goods_name.category

                        batch_tag = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"]
                        for tag in batch_tag:
                            batch_num = str(pre_year_num) + str(pre_week_num) + str(category) + str(goods_number) + str(tag)
                            if ManuOrderInfo.objects.filter(batch_num=batch_num).exists():
                                manufactory_order.batch_num = None
                                continue
                            else:
                                manufactory_order.batch_num = batch_num
                                break
                        if manufactory_order.batch_num is None:
                            self.message_user("存在异常订单 %s 请修正此订单之后再递交" % obj.planorder_id, "error")
                            continue

                        manufactory_machine_qs = GoodsToManufactoryInfo.objects.filter(goods_name=obj.goods_name)
                        if manufactory_machine_qs:
                            manufactory_order.manufactory = manufactory_machine_qs[0].manufactory
                        else:
                            self.message_user("此订单%s货品没有关联工程，请先设置货品关联工厂" % obj.planorder_id, "error")
                            n -= 1
                            obj.tag_sign = 3
                            obj.save()
                            continue

                        manufactory_order.estimated_time = estimated_time
                        manufactory_order.goods_id = obj.goods_name.goods_id
                        manufactory_order.goods_name = obj.goods_name.goods_name
                        manufactory_order.quantity = obj.quantity
                        manufactory_order.start_sn = batch_num + str("00001")

                        transition_num = 100000 + int(obj.quantity)
                        manufactory_order.end_sn = batch_num + str(transition_num)[-5:]

                        manufactory_order.creator = self.request.user.username

                        try:
                            manufactory_order.save()
                            # self.message_user("订单 %s 工厂订单创建完毕" % obj.planorder_id, 'success')
                            queryset.filter(planorder_id=obj.planorder_id).update(order_status=3)
                        except Exception as e:
                            obj.tag_sign = 4
                            n -= 1
                            obj.save()
                            self.message_user("订单 %s 创建错误，错误原因：%s" % (obj.planorder_id, e))

                        # 创建客供需求单
                        # parts_qs = PartToProductInfo.objects.filter(machine_name=obj.goods_name, status=1)
                        # if parts_qs:
                        #     num = 1
                        #     for part in parts_qs:
                        #         customer_requisition = CusRequisitionInfo()
                        #
                        #         if CusRequisitionInfo.objects.filter(batch_num=batch_num, goods_id=customer_requisition.goods_id).exists():
                        #             self.message_user("此订单%s,此货品%s,已经创建需求单，请不要重复递交" % (obj.planorder_id, customer_requisition.goods_id))
                        #             continue
                        #
                        #         prefix = "CQ"
                        #         serial_number = str(datetime.datetime.now())
                        #         serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(
                        #             ".", "")
                        #         serial_number = str(int(serial_number[0:17]) + num)
                        #         customer_requisition.cus_requisition_id = prefix + serial_number + "A"
                        #         customer_requisition.creator = self.request.user.username
                        #
                        #         customer_requisition.planorder_id = obj.planorder_id
                        #         customer_requisition.batch_num = batch_num
                        #         customer_requisition.quantity = obj.quantity
                        #         customer_requisition.estimated_time = estimated_time
                        #         customer_requisition.goods_id = part.part_name.goods_id
                        #         customer_requisition.goods_name = part.part_name.goods_name
                        #
                        #         manufactory_part_qs = GoodsToManufactoryInfo.objects.filter(goods_name=part.part_name)
                        #         if manufactory_part_qs:
                        #             customer_requisition.manufactory = manufactory_part_qs[0].manufactory
                        #         else:
                        #             self.message_user("注意：订单 %s 配件 %s 没有关联工厂，需要请设置货品关联工厂" % (obj.planorder_id, customer_requisition.goods_name), 'error')
                        #
                        #         try:
                        #             customer_requisition.save()
                        #             self.message_user("订单 %s 客供需求货品%s订单创建完毕" % (obj.planorder_id, customer_requisition.goods_name), 'success')
                        #         except Exception as e:
                        #             self.message_user("此订单%s的客户需求单，创建出错，错误原因：%s" % (obj.planorder_id, e))
                        #         num += 1
                        # else:
                        #     self.message_user("注意：订单 %s 生产的货品 %s 没有客供件" % (obj.planorder_id, obj.goods_name), 'error')

            self.message_user("成功处理完毕 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None

    def update_data(self, obj, target_obj):
        pass


class PlanOrderInfoAdmin(object):
    list_display = ["planorder_id","goods_name","quantity","estimated_time","order_status","category","creator"]
    list_filter = ["goods_name__goods_name", "category"]
    search_fields = ["planorder_id"]
    ordering = ["planorder_id"]
    readonly_fields = ["planorder_id","goods_name","quantity","estimated_time","order_status","category","creator"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class PlanOrderPenddingInfoAdmin(object):
    list_display = ["planorder_id","tag_sign","goods_name","quantity","estimated_time","order_status","category","creator"]
    list_filter = ["tag_sign","goods_name__goods_name", "category","order_status","category","create_time","update_time"]
    search_fields = ["planorder_id","goods_name__goods_name"]
    ordering = ["planorder_id"]
    form_layout = [
        Fieldset('必填信息',
                 'planorder_id', 'goods_name', "estimated_time", "quantity", "category"),
        Fieldset(None,
                 'creator', 'order_status', 'is_delete', **{"style": "display:None"}),
    ]

    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {
        "PO单号": "planorder_id",
        "期望到货时间": "estimated_time",
        "申请量": "quantity",
        "商家编码": "goods_id"
    }
    import_data = True

    actions = [CheckAction, RejectSelectedAction]

    def queryset(self):
        qs = super(PlanOrderPenddingInfoAdmin, self).queryset()
        qs = qs.filter(order_status=1)
        return qs

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.save()
        if obj.planorder_id is None:
            prefix = "PO"
            serial_number = str(datetime.datetime.now())
            serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
            obj.planorder_id = prefix + str(serial_number)[0:17] + "A"
            obj.save()
        super().save_models()

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('导入成功数据%s条' % int(result['successful']), 'success')
            if result['false'] > 0 or result['error']:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (int(result['false']), result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('包含更新重复数据%s条' % int(result['repeated']), 'error')
        return super(PlanOrderPenddingInfoAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0)

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = PlanOrderPenddingInfo.verify_mandatory(columns_key)
            if _ret_verify_field is not None:
                return report_dic['error'].append(_ret_verify_field)

            # 更改一下DataFrame的表名称
            columns_key_ori = df.columns.values.tolist()
            ret_columns_key = dict(zip(columns_key_ori, columns_key))
            df.rename(columns=ret_columns_key, inplace=True)

            # 更改一下DataFrame的表名称
            num_end = 0
            step = 300
            step_num = int(len(df) / step) + 2
            i = 1
            while i < step_num:
                num_start = num_end
                num_end = step * i
                intermediate_df = df.iloc[num_start: num_end]

                # 获取导入表格的字典，每一行一个字典。这个字典最后显示是个list
                _ret_list = intermediate_df.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(request, _ret_list)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
                i += 1
            return report_dic
        # 以下是csv处理逻辑，和上面的处理逻辑基本一致。
        elif '.' in _file.name and _file.name.rsplit('.')[-1] == 'csv':
            df = pd.read_csv(_file, encoding="GBK", chunksize=900)

            for piece in df:
                # 获取表头
                columns_key = piece.columns.values.tolist()
                # 剔除表头中特殊字符等于号和空格
                for i in range(len(columns_key)):
                    columns_key[i] = columns_key[i].replace(' ', '').replace('=', '')
                # 循环处理对应的预先设置，转换成数据库字段名称
                for i in range(len(columns_key)):
                    if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])
                # 直接调用验证函数进行验证
                _ret_verify_field = PlanOrderPenddingInfo.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field
                # 验证通过进行重新处理。
                columns_key_ori = piece.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                piece.rename(columns=ret_columns_key, inplace=True)
                _ret_list = piece.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(request, _ret_list)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
            return report_dic

        else:
            report_dic["error"].append('只支持excel和csv文件格式！')
            return report_dic

    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}

        # 开始导入数据
        for row in resource:
            if PlanOrderInfo.objects.filter(is_delete=0, planorder_id=row['planorder_id']).exists():
                report_dic["repeated"] += 1
                continue
            plan_order = PlanOrderInfo()  # 创建表格每一行为一个对象

            goods_id = row["goods_id"]
            goods_name = MachineInfo.objects.filter(goods_id=goods_id)
            if goods_name.exists():
                goods_name = goods_name[0]
                plan_order.goods_name = goods_name
            else:
                report_dic["error"].append("%s单据货品错误" % row["planorder_id"])
                report_dic["false"] += 1
                continue
            planorder_id = str(row["planorder_id"]).replace(" ", "")
            if re.match("^POA[0-9]+$", planorder_id):
                plan_order.planorder_id = planorder_id
            else:
                report_dic["error"].append("%s单据单号错误" % row["planorder_id"])
                report_dic["false"] += 1
                continue
            quantity = str(row["quantity"]).replace(" ", "")
            if re.match("^[0-9]+$", quantity):
                plan_order.quantity = int(quantity)
            else:
                report_dic["error"].append("%s单据数量错误" % row["planorder_id"])
                report_dic["false"] += 1
                continue
            estimated_time = row["estimated_time"]
            plan_order.estimated_time = estimated_time

            try:
                plan_order.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["false"] += 1
                report_dic["error"].append(e)
        return report_dic


class PlanOrderSubmitInfoAdmin(object):
    list_display = ["planorder_id","order_status","tag_sign","goods_name","quantity","estimated_time","category","creator"]
    list_filter = ["goods_name__goods_name", "category"]
    search_fields = ["planorder_id","goods_name__goods_name"]
    ordering = ["planorder_id"]
    actions = [SubmitActionPO, RejectSelectedAction]

    def queryset(self):
        qs = super(PlanOrderSubmitInfoAdmin, self).queryset()
        qs = qs.filter(order_status=2)
        return qs

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(PlanOrderPenddingInfo, PlanOrderPenddingInfoAdmin)
xadmin.site.register(PlanOrderSubmitInfo, PlanOrderSubmitInfoAdmin)
xadmin.site.register(PlanOrderInfo, PlanOrderInfoAdmin)




