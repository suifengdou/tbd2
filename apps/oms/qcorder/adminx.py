# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 10:20
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


from .models import QCOriInfo, QCInfo, QCSubmitOriInfo, QCSubmitInfo
from apps.wms.stockin.models import StockInInfo
from apps.base.relationship.models import ManufactoryToWarehouse
from apps.oms.manuorder.models import ManuOrderProcessingInfo


ACTION_CHECKBOX_NAME = '_selected_action'


# 原始质检单驳回审核
class RejectSelectedOriQCAction(BaseActionView):

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
                    self.message_user("%s 取消成功" % obj.qc_order_id, "success")
                elif obj.order_status == 2:
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 驳回上一级成功" % obj.qc_order_id, "success")
                elif obj.order_status == 3:
                    self.message_user("%s 已递交完成，请去验货明细表中驳回。" % obj.qc_order_id, "success")
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


# 质检单驳回审核
class RejectSelectedQCAction(BaseActionView):

    action_name = "reject_selected"
    description = '驳回选中的质检单'

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
                    ori_order = QCOriInfo.objects.filter(qc_order_id=obj.qc_order_id)[0]
                    ori_order.order_status = 1
                    ori_order.save()
                    obj.memorandum = "%s 取消了质检单号为：%s的质检单" % (str(self.request.user.username), obj.qc_order_id)
                    obj.qc_order_id = "DD" + str(datetime.datetime.now()).replace("-", "").replace(" ", "").replace(":", "").replace(".", "")[:14]
                    obj.order_status -= 1
                    obj.save()
                    self.log('change', '取消了质检单', obj)
                    self.message_user("%s 取消成功，原始质检单驳回到待递交界面" % obj.qc_order_id, "success")
                elif obj.order_status == 2:
                    self.message_user("%s 已递交完成，请去入库明细表中驳回。" % obj.qc_order_id, "error")
                    self.log('change', '取消质检单，但是失败了——_——', obj)
                    n -= 1
                else:
                    self.message_user("%s 内部错误，请联系管理员。" % obj.qc_order_id, "error")
                    n -= 1
                    self.log('change', '遇到一个内部错误，虽然操作失败了——_——，但是你发现了问题', obj)
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
    action_name = "submit_oriorder"
    description = "递交选中的质检单"
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
                         '批量修改了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(order_status=3)
            else:
                i = 0
                for obj in queryset:
                    i += 1
                    self.log('change', '', obj)
                    if QCInfo.objects.filter(qc_order_id=obj.qc_order_id).exists():
                        self.message_user("单号ID：%s，已经递交过质检单，此次未生成质检单" % obj.qc_order_id, "error")
                        n -= 1
                        obj.order_status = 2
                        obj.save()
                        continue
                    accumulation = int(obj.batch_num.completednum()) + int(obj.batch_num.processingnum())
                    if accumulation > obj.batch_num.quantity:
                        self.message_user("此原始质检单号ID：%s，验货数量超过了订单数量，请修正" % obj.qc_order_id, "error")
                        continue

                    qc_order = QCInfo()
                    warehouse_qs = ManufactoryToWarehouse.objects.filter(manufactory=obj.batch_num.manufactory)
                    if warehouse_qs:
                        warehouse = warehouse_qs[0].warehouse
                        qc_order.warehouse = warehouse
                    else:
                        self.message_user("此原始质检单号ID：%s，工厂未关联仓库，请添加工厂关联到仓库" % obj.qc_order_id, "error")
                        continue

                    atts = ["qc_order_id", "quantity", "check_quantity", "creator", "a_flaw", "b1_flaw", "b2_flaw",
                            "c_flaw", "memorandum", "result", "category"]
                    for i in atts:
                        # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
                        if hasattr(qc_order, i):
                            value = getattr(obj, i, None)
                            if value in ['nan', 'NaN', 'NaT', None]:
                                value = ''
                            setattr(qc_order, i, value)  # 更新对象属性为字典对应键值

                    qc_order.manufactory = obj.batch_num.manufactory
                    qc_order.qc_time = obj.qc_time.strftime("%Y-%m-%d")
                    qc_order.batch_num = obj.batch_num
                    qc_order.goods_name = obj.batch_num.goods_name
                    qc_order.goods_id = obj.batch_num.goods_id

                    qc_order.total_quantity = obj.batch_num.quantity
                    qc_order.accumulation = int(obj.batch_num.completednum()) + qc_order.quantity

                    try:
                        qc_order.save()
                        queryset.filter(id=obj.id).update(order_status=2)
                        self.message_user("ID：%s，递交质检单成功" % obj.qc_order_id, "success")
                    except Exception as e:
                        self.message_user("此原始质检单号ID：%s，递交到质检单明细出现错误，错误原因：%s" % (obj.qc_order_id, e))
                        continue

            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class SubmitSockInAction(BaseActionView):
    action_name = "submit_oriorder"
    description = "递交选中的质检单"
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
                         '批量修改了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(order_status=3)
            else:
                i = 0
                for obj in queryset:
                    i += 1
                    self.log('change', '', obj)
                    accumulation = int(obj.batch_num.completednum()) + int(obj.batch_num.processingnum())
                    if accumulation > obj.batch_num.quantity:
                        self.message_user("此原始质检单号ID：%s，验货数量超过了订单数量，请修正" % obj.qc_order_id, "error")
                        continue
                    if StockInInfo.objects.filter(source_order_id=obj.qc_order_id, order_status__in=[1, 2]).exists():
                        self.message_user("单号ID：%s，已经生成过入库单，此次未生成入库单" % obj.qc_order_id, "error")
                        n -= 1
                        obj.order_status = 2
                        obj.save()
                        continue
                    stockin_order = StockInInfo()
                    warehouse_qs = ManufactoryToWarehouse.objects.filter(manufactory=obj.batch_num.manufactory)
                    if warehouse_qs:
                        warehouse = warehouse_qs[0].warehouse
                        stockin_order.warehouse = warehouse
                    else:
                        self.message_user("此原始质检单号ID：%s，工厂未关联仓库，请添加工厂关联到仓库" % obj.qc_order_id, "error")
                        continue

                    prefix = "SI"
                    serial_number = str(datetime.datetime.now())
                    serial_number = int(serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")[0:16])
                    serial_number += i
                    stockin_order.stockin_id = prefix + str(serial_number) + "AQC"

                    stockin_order.category = 0
                    stockin_order.batch_num = obj.batch_num.batch_num
                    stockin_order.planorder_id = obj.batch_num.planorder_id
                    stockin_order.goods_name = obj.batch_num.goods_name
                    stockin_order.goods_id = obj.batch_num.goods_id
                    stockin_order.quantity = obj.quantity
                    stockin_order.source_order_id = obj.qc_order_id

                    try:
                        if obj.result == 1:
                            self.message_user("%s，验货失败质检单，不生成入库单" % obj.qc_order_id, "success")
                            n -= 1
                            obj.order_status = 2
                            obj.save()
                            continue
                        else:
                            stockin_order.save()
                            self.message_user("%s，生成入库单号：%s" % (obj.qc_order_id, stockin_order.stockin_id), "success")
                            obj.order_status = 2
                            obj.save()
                            continue
                    except Exception as e:
                        self.message_user("此原始质检单号ID：%s，出现错误， ：%s" % (obj.id, e), "error")
                        continue

            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class QCOriInfoAdmin(object):
    list_display = ['creator', "qc_order_id", "order_status", "batch_num","quantity","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum"]
    search_fields = ["batch_num"]
    readonly_fields = ["order_status", "batch_num","quantity","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum", 'creator', "qc_order_id"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class QCSubmitOriInfoAdmin(object):
    list_display = ['creator', "qc_order_id", "order_status", "batch_num","quantity","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum"]
    search_fields = ["batch_num"]
    readonly_fields = ['creator', "qc_order_id"]
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {
        '序号': 'null01',
        '日期': 'qc_date',
        '订单号': 'null02',
        '生产工厂': 'null03',
        '型号': 'null04',
        '订单数量': 'null05',
        '当天完成量': 'quantity',
        '累计完成': 'null06',
        '产品序列号范围': 'batch_num',
        '抽检数量': 'check_quantity',
        '检验结果': 'result',
        '验货次数': 'category',
        '检验员': 'creator',
        'A类缺陷': 'a_flaw',
        'B1类缺陷': 'b1_flaw',
        'B2类缺陷': 'b2_flaw',
        'C类缺陷': 'c_flaw',
        'DPU': 'null07',
        '主缺陷备注': 'memorandum',
        '月序列号': 'null08',
        'QC单号': 'qc_order_id'
                        }
    import_data = True

    actions = [SubmitAction, RejectSelectedOriQCAction]

    def queryset(self):
        qs = super(QCSubmitOriInfoAdmin, self).queryset()
        qs = qs.filter(order_status=1)
        return qs

    def save_models(self):
        obj = self.new_obj
        request = self.request
        if obj.qc_order_id is None:
            prefix = "QC"
            serial_number = str(datetime.datetime.now())
            serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
            obj.qc_order_id = prefix + serial_number[0:16] + "M"
            obj.creator = request.user.username
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
        return super(QCSubmitOriInfoAdmin, self).post(request, *args, **kwargs)

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
            _ret_verify_field = QCOriInfo.verify_mandatory(columns_key)
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
                _ret_verify_field = QCOriInfo.verify_mandatory(columns_key)
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
        category_dic = {'截单退回': 0, '无人收货': 1, '客户拒签': 2, '修改地址': 3, '催件派送': 4, '虚假签收': 5, '其他异常': 6}

        # 开始导入数据
        for row in resource:
            if QCOriInfo.objects.filter(is_delete=0, qc_order_id=row['qc_order_id'], order_status__in=[1, 2]).exists():
                report_dic["repeated"] += 1
                continue
            qc_order = QCOriInfo()  # 创建表格每一行为一个对象
            batch_num = str(row["batch_num"]).replace(" ", "")[:11]
            # 查询一下批次号，根据批次号查询
            check_batch = ManuOrderProcessingInfo.objects.filter(is_delete=0, batch_num=batch_num)
            if check_batch.exists():
                qc_order.batch_num = check_batch[0]
            else:
                report_dic['error'].append('不存批次号:%s，请检查修正源表' % batch_num)
                report_dic['false'] += 1
                continue
            if row['result'] == '合格':
                qc_order.result = 1
            else:
                qc_order.result = 0

            if row['category'] == 1:
                qc_order.category = 0
            else:
                qc_order.category = 1
            atts = ["qc_order_id", "quantity", "check_quantity", "creator", "a_flaw", "b1_flaw", "b2_flaw", "c_flaw", "memorandum"]
            for i in atts:
                # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
                if hasattr(qc_order, i):
                    value = row.get(i, None)
                    if value in ['nan', 'NaN', 'NaT', None]:
                        value = ''
                    setattr(qc_order, i, value)  # 更新对象属性为字典对应键值
            try:
                qc_order.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["false"] += 1
                report_dic["error"].append(e)
        return report_dic


class QCSubmitInfoAdmin(object):
    list_display = ["batch_num", "qc_order_id", "goods_name", "order_status", "manufactory", "goods_id", "quantity",
                    "total_quantity", "accumulation", "result", "category", "check_quantity", "a_flaw", "b1_flaw",
                    "b2_flaw", "c_flaw", "memorandum"]
    list_filter = ["goods_name", "manufactory", "goods_id", "category"]
    actions = [SubmitSockInAction, RejectSelectedQCAction]

    def queryset(self):
        qs = super(QCSubmitInfoAdmin, self).queryset()
        qs= qs.filter(order_status=1)
        return qs

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class QCInfoAdmin(object):
    list_display = ["batch_num","qc_order_id","goods_name","order_status","manufactory","goods_id","quantity","total_quantity","accumulation","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum"]
    list_filter = ["goods_name", "manufactory", "goods_id", "category"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(QCSubmitOriInfo, QCSubmitOriInfoAdmin)
xadmin.site.register(QCOriInfo, QCOriInfoAdmin)
xadmin.site.register(QCSubmitInfo, QCSubmitInfoAdmin)
xadmin.site.register(QCInfo, QCInfoAdmin)






