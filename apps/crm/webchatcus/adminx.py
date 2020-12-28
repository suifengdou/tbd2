# -*- coding: utf-8 -*-
# @Time    : 2020/12/11 18:44
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import math, re
import datetime
import pandas as pd
import emoji
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse
from django.db.models import Sum, Avg, Min, Max, F, Count

from django.contrib.admin.utils import get_deleted_objects

from django.core.files.uploadedfile import InMemoryUploadedFile

import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side

from .models import OWOrder, OriWebchatInfo, WOrder, WebchatInfo, OWNumber, OriWarrantyInfo, WNumber, WarrantyInfo, WebchatCus
from apps.crm.customers.models import CustomerInfo
from apps.crm.services.models import ServicesDetail


ACTION_CHECKBOX_NAME = '_selected_action'


class RejectSelectedAction(BaseActionView):

    action_name = "reject_selected"
    description = '驳回选中的单据'

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

                if isinstance(obj, OriWebchatInfo):
                    obj.order_status -= 1
                    obj.process_tag = 5
                    if obj.order_status == 0:
                        self.message_user("%s 取消成功" % obj.cs_mobile, "success")
                    obj.save()

                if isinstance(obj, WebchatInfo):
                    obj.order_status -= 1
                    obj.process_tag = 5
                    if obj.order_status == 0:
                        self.message_user("%s 取消成功" % obj.customer, "success")
                    obj.save()

                if isinstance(obj, OriWarrantyInfo):
                    obj.order_status -= 1
                    obj.process_tag = 5
                    if obj.order_status == 0:
                        self.message_user("%s 取消成功" % obj.smartphone, "success")
                    obj.save()

                if isinstance(obj, WarrantyInfo):
                    obj.order_status -= 1
                    obj.process_tag = 5
                    if obj.order_status == 0:
                        self.message_user("%s 取消成功" % obj.customer, "success")
                    obj.save()

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


# 递交原始微信公众号注册信息
class SubmitOWAction(BaseActionView):
    action_name = "submit_ori_ow"
    description = "提交选中的单据"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(order_status=3)
            else:
                for obj in queryset:
                    self.log('change', '%s递交了原始微信信息' % self.request.user.username, obj)
                    webchat_order = WebchatInfo()

                    _q_order_list = CustomerInfo.objects.filter(mobile=obj.cs_mobile)
                    if _q_order_list.exists():
                        webchat_order.customer = _q_order_list[0]
                    else:
                        customer = CustomerInfo()
                        customer.mobile = obj.cs_mobile
                        if obj.nick_name:
                            customer.webchat = obj.nick_name
                        customer.total_times = 1
                        customer.save()
                        webchat_order.customer = customer

                    _q_webchat_cus = WebchatCus.objects.filter(customer=webchat_order.customer)
                    if not _q_webchat_cus.exists():
                        webchat_cus = WebchatCus()
                        webchat_cus.customer = webchat_order.customer
                        webchat_cus.save()

                    fields_list = ['type', 'goods_name', 'goods_series', 'goods_id', 'produce_sn',
                                   'activity_time', 'purchase_time', 'comment', 'register_time', 'cs_id',
                                   'nick_name', 'area', 'gender', 'name', 'cs_gender', 'cs_area',
                                   'cs_address', 'living_area', 'family', 'habit', 'other_habit']

                    for field in fields_list:
                        setattr(webchat_order, field, getattr(obj, field, None))
                    try:
                        webchat_order.creator = self.request.user.username
                        webchat_order.save()
                        obj.order_status = 2
                        obj.mistake_tag = 0
                        obj.save()
                    except Exception as e:
                        n -= 1
                        self.message_user("%s递交错误：%s" % (obj.cs_mobile, e), "error")
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 匹配微信公众号注册信息
class CheckWAction(BaseActionView):
    action_name = "check_wo"
    description = "过滤待完成的任务"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(order_status=3)
            else:
                for obj in queryset:
                    self.log('change', '%s过滤了微信客户信息' % self.request.user.username, obj)
                    _q_detail_list = ServicesDetail.objects.filter(customer=obj.customer, order_status__in=[2, 3],
                                                                   order_type=2)
                    if _q_detail_list.exists():
                        for detail in _q_detail_list:
                            detail.order_status = 5
                            detail.process_tag = 7
                            detail.save()
                    obj.order_status = 2
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 递交微信公众号注册信息
class SubmitOWNAction(BaseActionView):
    action_name = "submit_ori_nuber"
    description = "提交选中的单据"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(order_status=3)
            else:
                for obj in queryset:
                    self.log('change', '%s递交了原始微信信息' % self.request.user.username, obj)
                    warranty_order = WarrantyInfo()

                    _q_order_list = CustomerInfo.objects.filter(mobile=obj.smartphone)
                    if _q_order_list.exists():
                        warranty_order.customer = _q_order_list[0]
                    else:
                        n -= 1
                        self.message_user("先创建客户档案：%s" % obj.smartphone, "error")
                        obj.mistake_tag = 2
                        obj.save()
                        continue

                    fields_list = ['warranty_sn', 'batch_name', 'duration', 'goods_name', 'produce_sn',
                                   'purchase_time', 'register_time', 'webchat_name', 'name',
                                   'gender', 'area', 'living_area', 'family', 'habit', 'other_habit']

                    for field in fields_list:
                        setattr(warranty_order, field, getattr(obj, field, None))
                    try:
                        warranty_order.creator = self.request.user.username
                        warranty_order.save()
                        obj.order_status = 2
                        obj.mistake_tag = 0
                        obj.save()
                    except Exception as e:
                        n -= 1
                        self.message_user("%s递交错误：%s" % (obj.cs_mobile, e), "error")
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 匹配微信公众号注册信息
class CheckWNAction(BaseActionView):
    action_name = "check_wo_nuber"
    description = "过滤待完成的任务"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(order_status=3)
            else:
                for obj in queryset:
                    self.log('change', '%s过滤了微信客户信息' % self.request.user.username, obj)
                    _q_detail_list = ServicesDetail.objects.filter(warranty_sn=obj.warranty_sn,
                                                                   order_status__in=[2, 3],
                                                                   order_type=2)
                    if _q_detail_list.exists():
                        for detail in _q_detail_list:
                            detail.order_status = 5
                            detail.process_tag = 7
                            detail.save()
                    obj.order_status = 2
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 导入原始微信公众号注册信息
class OWOrderAdmin(object):
    list_display = ['type', 'goods_code', 'goods_name', 'goods_series', 'goods_id', 'produce_year',
                    'produce_week', 'produce_batch', 'produce_sn', 'activity_time',
                    'purchase_time', 'grade', 'comment', 'register_time', 'cs_id', 'nick_name', 'area',
                    'gender', 'check_status', 'name', 'cs_gender', 'cs_mobile', 'cs_area',
                    'cs_address', 'living_area', 'family', 'habit', 'other_habit', 'auth_time']
    list_filter = ['type', 'goods_code', 'goods_name', 'goods_series', 'goods_id', 'produce_year', 'cs_mobile',
                   'produce_sn', 'create_time', 'creator']
    actions = [SubmitOWAction, RejectSelectedAction]

    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    INIT_FIELDS_DIC = {
        '机器类别': 'type',
        '产品ID': 'goods_code',
        '产品名称': 'goods_name',
        '货品序号': 'goods_series',
        '型号': 'goods_id',
        '生产年': 'produce_year',
        '生产周': 'produce_week',
        '周批次': 'produce_batch',
        '码值': 'produce_sn',
        '激活时间': 'activity_time',
        '购买日期': 'purchase_time',
        '评价星级（1-5）': 'grade',
        '评论内容': 'comment',
        '产品注册时间': 'register_time',
        '用户id': 'cs_id',
        '昵称': 'nick_name',
        '所在地区': 'area',
        '性别': 'gender',
        '审核状态': 'check_status',
        '真实姓名': 'name',
        '真实性别': 'cs_gender',
        '真实手机号': 'cs_mobile',
        '真实区域': 'cs_area',
        '真实地址': 'cs_address',
        '家庭面积': 'living_area',
        '家庭成员': 'family',
        '兴趣爱好': 'habit',
        '其他兴趣': 'other_habit',
        '授权时间': 'auth_time',
    }

    import_data = True


    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('结果提示：%s' % result)
        return super(OWOrderAdmin, self).post(request, *args, **kwargs)


    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ['机器类别', '产品ID', '产品名称', '货品序号', '型号', '生产年', '生产周', '周批次',
                             '码值', '激活时间', '购买日期', '评价星级（1-5）', '评论内容', '产品注册时间',
                             '用户id', '昵称', '所在地区', '性别', '审核状态', '真实姓名', '真实性别',
                             '真实手机号', '真实区域', '真实地址', '家庭面积', '家庭成员', '兴趣爱好', '其他兴趣', '授权时间']

            try:
                df = df[FILTER_FIELDS]
            except Exception as e:
                report_dic["error"].append(e)
                return report_dic

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = OWOrder.verify_mandatory(columns_key)
            if _ret_verify_field is not None:
                return _ret_verify_field

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
            df = pd.read_csv(_file, encoding="GBK", chunksize=300, dtype=str)

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
                _ret_verify_field = OWOrder.verify_mandatory(columns_key)
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
            report_dic["error"].append('只支持excel文件格式！')
            return report_dic


    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        for row in resource:
            if not re.match('^1[3-9][0-9]{9}$', str(row['cs_mobile'])):
                report_dic['error'].append("电话不符合规则，无法导入")
                report_dic["false"] += 1
                continue
            # row['purchase_time'] = str(row['purchase_time'] + ':00').replace('/', '-')
            # row['register_time'] = str(row['register_time'] + ':00').replace('/', '-')
            # row['auth_time'] = str(row['auth_time'] + ':00').replace('/', '-')
            row['activity_time'] = row['activity_time'].replace('T', ' ').replace('Z', '')
            emo_fields = ['nick_name', 'comment', 'name', 'cs_address', 'living_area']
            for word in emo_fields:
                row[word] = emoji.demojize(str(row[word]))
            order_fields = ['type', 'goods_code', 'goods_name', 'goods_series', 'goods_id', 'produce_year',
                            'produce_week', 'produce_batch', 'produce_sn', 'activity_time',
                            'purchase_time', 'grade', 'comment', 'register_time', 'cs_id', 'nick_name', 'area',
                            'gender', 'check_status', 'name', 'cs_gender', 'cs_mobile', 'cs_area',
                            'cs_address', 'living_area', 'family', 'habit', 'other_habit', 'auth_time']
            order = OriWebchatInfo()
            for field in order_fields:
                if str(row[field]) in ['nan', 'NaN']:
                    row[field] = ''
                setattr(order, field, row[field])

            try:
                order.creator = request.user.username
                order.save()
                report_dic["successful"] += 1
            except Exception as e:
                report_dic['error'].append(e)
                report_dic["false"] += 1

        return report_dic


    def queryset(self):
        queryset = super(OWOrderAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset


    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 原始微信公众号注册信息查询
class OriWebchatInfoAdmin(object):
    list_display = ['type', 'goods_code', 'goods_name', 'goods_series', 'goods_id', 'produce_year',
                    'produce_week', 'produce_batch', 'produce_sn', 'activity_time',
                    'purchase_time', 'grade', 'comment', 'register_time', 'cs_id', 'nick_name', 'area',
                    'gender', 'check_status', 'name', 'cs_gender', 'cs_mobile', 'cs_area',
                    'cs_address', 'living_area', 'family', 'habit', 'other_habit', 'auth_time']

    list_filter = ['type', 'goods_code', 'goods_name', 'goods_series', 'goods_id', 'produce_year', 'cs_mobile',
                   'produce_sn', 'create_time', 'creator']

    readonley_fields = ['type', 'goods_code', 'goods_name', 'goods_series', 'goods_id', 'produce_year',
                        'produce_week', 'produce_batch', 'produce_sn', 'activity_time',
                        'purchase_time', 'grade', 'comment', 'register_time', 'cs_id', 'nick_name', 'area',
                        'gender', 'check_status', 'name', 'cs_gender', 'cs_mobile', 'cs_area',
                        'cs_address', 'living_area', 'family', 'habit', 'other_habit', 'auth_time',
                        'creator', 'create_time', 'update_time', 'is_delete']

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick',),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile',),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ),),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]


    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 微信公众号注册信息
class WOrderAdmin(object):
    list_display = ['customer', 'type', 'goods_name', 'goods_series', 'goods_id', 'produce_sn', 'activity_time',
                    'purchase_time', 'comment', 'register_time', 'cs_id', 'nick_name', 'area', 'gender',
                    'name', 'cs_gender', 'cs_area', 'cs_address', 'living_area', 'family', 'habit', 'other_habit']

    list_filter = []
    actions = [CheckWAction, RejectSelectedAction]
    readonley_fields = []

    # form_layout = [
    #     Fieldset('基本信息',
    #              Row('shop_name', 'warehouse_name', 'buyer_nick', ),
    #
    #              Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
    #              Row('goods_name', 'spec_code', 'num',
    #                  'price', 'share_amount', ),
    #              Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
    #     Fieldset(None,
    #              'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    # ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 微信公众号注册信息查询
class WebchatInfoAdmin(object):
    list_display = ['customer', 'type', 'goods_name', 'goods_series', 'goods_id', 'produce_sn', 'activity_time',
                    'purchase_time', 'comment', 'register_time', 'cs_id', 'nick_name', 'area', 'gender',
                    'name', 'cs_gender', 'cs_area', 'cs_address', 'living_area', 'family', 'habit', 'other_habit']

    list_filter = []

    readonley_fields = []

    # form_layout = [
    #     Fieldset('基本信息',
    #              Row('shop_name', 'warehouse_name', 'buyer_nick', ),
    #
    #              Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
    #              Row('goods_name', 'spec_code', 'num',
    #                  'price', 'share_amount', ),
    #              Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
    #     Fieldset(None,
    #              'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    # ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 原始延保码导入
class OWNumberAdmin(object):
    list_display = ['warranty_sn', 'process_tag', 'mistake_tag', 'batch_name', 'duration', 'goods_name', 'produce_sn',
                    'purchase_time', 'register_time', 'webchat_name', 'name',
                    'gender', 'smartphone', 'area', 'living_area', 'family', 'habit', 'other_habit']

    list_filter = ['process_tag', 'mistake_tag', 'warranty_sn', 'batch_name', 'goods_name',
                   'produce_sn', 'purchase_time', 'register_time', 'smartphone', 'creator', 'create_time']
    actions = [SubmitOWNAction, RejectSelectedAction]

    form_layout = [
        Fieldset('基本信息',
                 Row('batch_name', 'warranty_sn', 'produce_sn', ),

                 Row('duration', 'warranty_sn',),
                 Row('goods_name', 'purchase_time', 'register_time',
                     'webchat_name', 'name', ),),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    INIT_FIELDS_DIC = {
        '延保码': 'warranty_sn',
        '所属批次': 'batch_name',
        '延保时长': 'duration',
        '商品型号': 'goods_name',
        '序列号': 'produce_sn',
        '购买时间': 'purchase_time',
        '产品注册时间': 'register_time',
        '微信昵称': 'webchat_name',
        '姓名': 'name',
        '生日': 'birthday',
        '性别': 'gender',
        '手机号': 'smartphone',
        '地区': 'area',
        '家庭面积': 'living_area',
        '家庭成员': 'family',
        '兴趣领域': 'habit',
        '其他兴趣': 'other_habit',
    }

    import_data = True

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('结果提示：%s' % result)
        return super(OWNumberAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ['延保码', '所属批次', '延保时长', '商品型号', '序列号', '购买时间',
                             '产品注册时间', '微信昵称', '姓名', '生日', '性别', '手机号', '地区',
                             '家庭面积', '家庭成员', '兴趣领域', '其他兴趣']

            try:
                df = df[FILTER_FIELDS]
            except Exception as e:
                report_dic["error"].append(e)
                return report_dic

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = OWNumber.verify_mandatory(columns_key)
            if _ret_verify_field is not None:
                return _ret_verify_field

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
            df = pd.read_csv(_file, encoding="GBK", chunksize=300, dtype=str)

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
                _ret_verify_field = OWNumber.verify_mandatory(columns_key)
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
            report_dic["error"].append('只支持excel文件格式！')
            return report_dic


    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        for row in resource:
            _q_warranty_sn = OriWarrantyInfo.objects.filter(warranty_sn=row['warranty_sn'])
            if _q_warranty_sn.exists():
                report_dic['error'].append("%s 已经存在" % row['warranty_sn'])
                report_dic["repeated"] += 1
                continue
            if not re.match('^1[3-9][0-9]{9}$', str(row['smartphone'])):
                report_dic['error'].append("%s 电话不符合规则，无法导入" % str(row['smartphone']))
                report_dic["false"] += 1
                continue
            emo_fields = ['name', 'webchat_name']
            for word in emo_fields:
                row[word] = emoji.demojize(str(row[word]))
            row['duration'] = str(row['duration']).replace('天', '')
            #
            # row['purchase_time'] = str(row['purchase_time'] + ':00').replace('/', '-')
            # row['register_time'] = str(row['register_time'] + ':00').replace('/', '-')
            order_fields = ['warranty_sn', 'batch_name', 'duration', 'goods_name', 'produce_sn',
                            'purchase_time', 'register_time', 'webchat_name', 'name',
                            'gender', 'smartphone', 'area', 'living_area', 'family', 'habit', 'other_habit']
            order = OriWarrantyInfo()
            for field in order_fields:
                if str(row[field]) in ['nan', 'NaN']:
                    row[field] = ''
                setattr(order, field, row[field])

            try:
                order.creator = request.user.username
                order.save()
                report_dic["successful"] += 1
            except Exception as e:
                report_dic['error'].append(e)
                report_dic["false"] += 1

        return report_dic

    def queryset(self):
        queryset = super(OWNumberAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 原始延保码查询
class OriWarrantyInfoAdmin(object):
    list_display = ['warranty_sn', 'batch_name', 'duration', 'goods_name', 'produce_sn',
                    'purchase_time', 'register_time', 'webchat_name', 'name',
                    'gender', 'smartphone', 'area', 'living_area', 'family', 'habit', 'other_habit']

    list_filter = ['process_tag', 'mistake_tag', 'warranty_sn', 'batch_name', 'goods_name',
                   'produce_sn', 'purchase_time', 'register_time', 'smartphone', 'creator', 'create_time']
    readonly_fields = []

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 延保码处理
class WNumberAdmin(object):
    list_display = ['customer', 'warranty_sn', 'batch_name', 'duration', 'goods_name', 'produce_sn',
                    'purchase_time', 'register_time', 'webchat_name', 'name',
                    'gender', 'area', 'living_area', 'family', 'habit', 'other_habit']
    list_filter = ['process_tag', 'mistake_tag', 'customer__mobile', 'warranty_sn', 'batch_name', 'goods_name',
                   'produce_sn', 'purchase_time', 'register_time', 'creator', 'create_time']

    actions = [CheckWNAction, RejectSelectedAction]
    form_layout = [
        Fieldset('基本信息',
                 Row('batch_name', 'warranty_sn', 'produce_sn', ),

                 Row('duration', 'warranty_sn',),
                 Row('goods_name', 'purchase_time', 'register_time',
                     'webchat_name', 'name', ),),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]
    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 延保码查询
class WarrantyInfoAdmin(object):
    def has_add_permission(self):
        # 禁用添加按钮
        return False


class WebchatCusAdmin(object):
    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(OWOrder, OWOrderAdmin)
xadmin.site.register(OriWebchatInfo, OriWebchatInfoAdmin)
xadmin.site.register(WOrder, WOrderAdmin)
xadmin.site.register(WebchatInfo, WebchatInfoAdmin)

xadmin.site.register(OWNumber, OWNumberAdmin)
xadmin.site.register(OriWarrantyInfo, OriWarrantyInfoAdmin)
xadmin.site.register(WNumber, WNumberAdmin)
xadmin.site.register(WarrantyInfo, WarrantyInfoAdmin)

xadmin.site.register(WebchatCus, WebchatCusAdmin)

