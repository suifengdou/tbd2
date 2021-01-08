# -*- coding: utf-8 -*-
# @Time    : 2020/4/24 16:07
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import math, re
import datetime
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse

from django.contrib.admin.utils import get_deleted_objects

import pandas as pd
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side
import emoji

from .models import DialogTag, OriDialogTB, OriDetailTB, OriDialogJD, OriDetailJD, ServicerInfo, MyExtractODTB
from .models import SensitiveInfo, CheckODJD, ExtractODJD, ExceptionODJD, CheckODTB, ExtractODTB, ExceptionODTB
from .models import OriDialogOW, OriDetailOW, CheckODOW, ExtractODOW, MyExtractODOW, ExceptionODOW, DOWID
from apps.base.shop.models import ShopInfo
from apps.assistants.giftintalk.models import GiftInTalkInfo, OrderTBList, OrderJDList, OrderOWList
from apps.assistants.compensation.models import OriCompensation, DiaToOriist
from apps.base.goods.models import MachineInfo

ACTION_CHECKBOX_NAME = '_selected_action'


# 对话标签界面
class DialogTagAdmin(object):
    list_display = ['name', 'category', 'order_status']


# 客服信息界面
class ServicerInfoAdmin(object):
    list_display =['name', 'platform', 'username', 'category']


# 敏感字管理界面
class SensitiveInfoAdmin(object):
    list_display = ['words', 'index_num', 'category', 'order_status']
    search_fields = ['words']
    list_filter = ['index_num', 'category', 'order_status']

    import_data = True

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(file)
            if isinstance(result, int):
                self.message_user('导入成功数据%s条' % result['successful'], 'success')
                if result['false'] > 0:
                    self.message_user('导入失败数据%s条,主要的错误是%s' % (result['false'], result['error']), 'warning')
                if result['repeated'] > 0:
                    self.message_user('包含更新重复数据%s条' % result['repeated'], 'error')
            else:
                self.message_user('结果提示：%s' % result)
        return super(SensitiveInfoAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, _file):
        INIT_FIELDS_DIC = {
            '敏感字': 'words',
            '指数': 'index_num',
        }

        ALLOWED_EXTENSIONS = ['xls', 'xlsx']
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        if '.' in _file.name and _file.name.rsplit('.')[-1] in ALLOWED_EXTENSIONS:
            with pd.ExcelFile(_file) as xls:
                df = pd.read_excel(xls, sheet_name=0)
                FILTER_FIELDS = ['敏感字', '指数']

                try:
                    df = df[FILTER_FIELDS]
                except Exception as e:
                    report_dic["error"].append(e)
                    return report_dic

                # 获取表头，对表头进行转换成数据库字段名
                columns_key = df.columns.values.tolist()
                for i in range(len(columns_key)):
                    columns_key[i] = columns_key[i].replace(' ', '').replace('=', '')

                for i in range(len(columns_key)):
                    if INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = INIT_FIELDS_DIC.get(columns_key[i])

                # 验证一下必要的核心字段是否存在
                _ret_verify_field = SensitiveInfo.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field

                # 更改一下DataFrame的表名称
                columns_key_ori = df.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                df.rename(columns=ret_columns_key, inplace=True)

                # 获取导入表格的字典，每一行一个字典。这个字典最后显示是个list
                _ret_list = df.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(_ret_list)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
                return report_dic

        # 以下是csv处理逻辑，和上面的处理逻辑基本一致。
        elif '.' in _file.name and _file.name.rsplit('.')[-1] == 'csv':
            df = pd.read_csv(_file, encoding="GBK", chunksize=300)

            for piece in df:
                # 获取表头
                columns_key = piece.columns.values.tolist()
                # 剔除表头中特殊字符等于号和空格
                for i in range(len(columns_key)):
                    columns_key[i] = columns_key[i].replace(' ', '').replace('=', '')
                # 循环处理对应的预先设置，转换成数据库字段名称
                for i in range(len(columns_key)):
                    if INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = INIT_FIELDS_DIC.get(columns_key[i])
                # 直接调用验证函数进行验证
                _ret_verify_field = SensitiveInfo.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field
                # 验证通过进行重新处理。
                columns_key_ori = piece.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                piece.rename(columns=ret_columns_key, inplace=True)
                _ret_list = piece.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(_ret_list)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
            return report_dic

        else:
            return "只支持excel和csv文件格式！"

    def save_resources(self, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        # 开始导入数据
        for row in resource:
            # 判断表格尾部
            for k, v in row.items():
                if re.match(r'^=', str(v)):
                    row[k] = v.replace('=', '').replace('"', '').replace(' ', '')

            order = SensitiveInfo()  # 创建表格每一行为一个对象

            for k, v in row.items():
                # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
                if hasattr(order, k):
                    if str(v) in ['nan', 'NaT']:
                        pass
                    else:
                        setattr(order, k, v)  # 更新对象属性为字典对应键值
            try:
                order.creator = self.request.user.username
                order.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["error"].append(e)
                report_dic["false"] += 1
        return report_dic

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.save()
        super().save_models()


# DFA算法，过滤关键字
class DFAFilter(object):
    def __init__(self):
        self.keyword_chains = {}  # 关键词链表
        self.delimit = '\x00'  # 限定

    def add(self, sensitive: object) -> object:
        keyword = sensitive.words  # 关键词英文变为小写
        chars = keyword.strip()  # 关键字去除首尾空格和换行
        if not chars:  # 如果关键词为空直接返回
            return
        level = self.keyword_chains
        # 遍历关键字的每个字
        for i in range(len(chars)):
            # 如果这个字已经存在字符链的key中就进入其子字典
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: sensitive.index_num}
                break
        if i == len(chars) - 1:
            level[self.delimit] = sensitive.index_num

    def parse(self, queryset):
        for sensitive in queryset:
            self.add(sensitive)

    def filter(self, obj):
        start = 0
        if obj.sensitive_tag == 1:
            return 0
        while start < len(obj.content):
            level = self.keyword_chains
            step_ins = 0
            for char in obj.content[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        obj.index_num += level[char][self.delimit]
                        start += step_ins - 1
                        break
                else:
                    break
            start += 1
        try:
            obj.sensitive_tag = 1
            obj.save()
        except Exception as e:
            return 0
        return 1


# 对话内容敏感字检查
class CheckAction(BaseActionView):
    action_name = "check_dialog_content"
    description = "过滤选中的对话敏感字"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            filter_task = DFAFilter()
            init_sensitive = SensitiveInfo.objects.filter(is_delete=0, order_status=1)
            if init_sensitive.exists():
                filter_task.parse(init_sensitive)
                success_num = 0
                for obj in queryset:
                    success_num += int(filter_task.filter(obj))
            else:
                self.message_user("没有过滤列表。", 'error')
                return None
            self.message_user("提交 %(count)d %(items)s。完成%(success_num)s" % { "count": n,
                                                                                "items": model_ngettext(self.opts, n),
                                                                                "success_num": success_num}, 'success')

        return None


# 对话详情页重置提取
class ResetODJDExtract(BaseActionView):
    action_name = "reset_dialog_extract"
    description = "重置选中的对话未提取"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            self.log('change',
                     '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
            queryset.update(extract_tag=0)
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 对话详情页重置敏感字
class ResetODJDSensitive(BaseActionView):
        action_name = "reset_dialog_check"
        description = "重置选中的对话过滤"
        model_perm = 'change'
        icon = "fa fa-check-square-o"

        @filter_hook
        def do_action(self, queryset):
            if not self.has_change_permission():
                raise PermissionDenied
            n = queryset.count()
            if n:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(sensitive_tag=0)
                self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
            return None


# 京东对话明细提取订单
class ExtractODJDAction(BaseActionView):
    action_name = "extract_dialog_content"
    description = "提取选中的对话"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    modify_models_batch = False



    @filter_hook
    def do_action(self, queryset):
        _rt_talk_title_new = ['order_category', 'servicer', 'goods', 'nickname', 'order_id', 'cs_information']
        _rt_talk_title_total = ['order_category', 'servicer', 'goods', 'nickname', 'order_id', 'cs_information',
                                'm_sn', 'broken_part', 'description']
        result = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            queryset.filter(d_status=1).update(extract_tag=1)
            queryset = queryset.filter(d_status=0)
            for obj in queryset:
                if OrderJDList.objects.filter(talk_jd=obj).exists():
                    result["discard"] += 1
                    obj.mistake_tag = 2
                    obj.save()
                    continue
                else:
                    order_list_jd = OrderJDList()
                _check_talk_data = re.findall(r'(·客服.*{.*}[\s\S]*?收货信息.*})', str(obj.content), re.DOTALL)
                if _check_talk_data:
                    _rt_talk = GiftInTalkInfo()
                    _rt_talk.platform = 2
                    _rt_talk_data = re.findall(r'{((?:.|\n)*?)}', str(obj.content), re.DOTALL)

                    if len(_rt_talk_data) == 6:
                        _rt_talk.platform = 2
                        _rt_talk_dic = dict(zip(_rt_talk_title_new, _rt_talk_data))
                        for k, v in _rt_talk_dic.items():
                            if hasattr(_rt_talk, k):
                                setattr(_rt_talk, k, v)
                    elif len(_rt_talk_data) == 9:
                        _rt_talk.platform = 2
                        _rt_talk_dic = dict(zip(_rt_talk_title_total, _rt_talk_data))
                        for k, v in _rt_talk_dic.items():
                            if hasattr(_rt_talk, k):
                                setattr(_rt_talk, k, v)

                    else:
                        result['false'] += 1
                        result['error'].append("%s 对话的格式不对，导致无法提取" % _rt_talk_data[1])
                        obj.category = 1
                        obj.mistake_tag = 1
                        obj.save()
                        continue
                    try:
                        _rt_talk.shop = obj.dialog_jd.shop
                        _rt_talk.creator = self.request.user.username
                        _rt_talk.save()
                        order_list_jd.gift_order = _rt_talk
                        order_list_jd.talk_jd = obj
                        order_list_jd.creator = self.request.user.username
                        order_list_jd.save()
                        result["successful"] += 1
                        obj.category = 1
                    except Exception as e:
                        result["false"] += 1
                        result["error"].append(e)
                        obj.mistake_tag = 1
                        obj.category = 1
                        obj.save()
                        continue
                obj.extract_tag = 1
                obj.save()
            self.message_user(result)
            self.message_user("提交 %(count)d %(items)s。" % {"count": n, "items": model_ngettext(self.opts, n)}, 'success')

        return None


# 淘宝对话明细提取订单
class ExtractODTBAction(BaseActionView):
    action_name = "extract_dialog_content_tb"
    description = "提取选中的对话"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        _rt_talk_title_new = ['order_category', 'servicer', 'goods', 'order_id', 'cs_information']
        _rt_talk_title_total = ['order_category', 'servicer', 'goods', 'order_id', 'cs_information',
                                'm_sn', 'broken_part', 'description']
        result = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            queryset.filter(d_status=1).update(extract_tag=1)
            queryset = queryset.filter(d_status=0)
            for obj in queryset:
                if OrderTBList.objects.filter(talk_tb=obj).exists():
                    result["discard"] += 1
                    obj.mistake_tag = 2
                    obj.save()
                    continue
                else:
                    order_list_tb = OrderTBList()
                _check_talk_data = re.findall(r'(·客服.*{.*}[\s\S]*?.*})', str(obj.content), re.DOTALL)
                if _check_talk_data:
                    _rt_talk = GiftInTalkInfo()
                    _rt_talk.platform = 1
                    _rt_talk_data = re.findall(r'{((?:.|\n)*?)}', str(obj.content), re.DOTALL)

                    if len(_rt_talk_data) == 5:
                        _rt_talk.platform = 1
                        _rt_talk_dic = dict(zip(_rt_talk_title_new, _rt_talk_data))
                        for k, v in _rt_talk_dic.items():
                            if hasattr(_rt_talk, k):
                                setattr(_rt_talk, k, v)
                    elif len(_rt_talk_data) == 8:
                        _rt_talk.platform = 1
                        _rt_talk_dic = dict(zip(_rt_talk_title_total, _rt_talk_data))
                        for k, v in _rt_talk_dic.items():
                            if hasattr(_rt_talk, k):
                                setattr(_rt_talk, k, v)

                    else:
                        result['false'] += 1
                        result['error'].append("%s 对话的格式不对，导致无法提取" % _rt_talk_data[1])
                        obj.category = 1
                        obj.mistake_tag = 1
                        obj.save()
                        continue
                    try:
                        _rt_talk.shop = obj.dialog_tb.shop
                        _rt_talk.creator = self.request.user.username
                        _rt_talk.nickname = '客户ID%s' % obj.dialog_tb.customer
                        _rt_talk.save()
                        order_list_tb.gift_order = _rt_talk
                        order_list_tb.talk_tb = obj
                        order_list_tb.creator = self.request.user.username
                        order_list_tb.save()
                        obj.category = 1
                        result["successful"] += 1
                    except Exception as e:
                        result["false"] += 1
                        result["error"].append(e)
                        obj.mistake_tag = 1
                        obj.category = 1
                        obj.save()
                        continue

                _compensation_talk_data = re.findall(r'(·您好{.*}[\s\S]*?.*})', str(obj.content), re.DOTALL)
                if _compensation_talk_data:
                    _q_com_repeat = DiaToOriist.objects.filter(dialog_order=obj)
                    if _q_com_repeat:
                        result["false"] += 1
                        obj.mistake_tag = 2
                        obj.category = 2
                        obj.save()
                        continue
                    else:
                        _com_dia_list = DiaToOriist()
                    _com_talk = OriCompensation()
                    _rt_com_talk = re.findall(r'{((?:.|\n)*?)}', str(obj.content), re.DOTALL)

                    if len(_rt_com_talk) == 8:
                        _com_talk.servicer = _rt_com_talk[0]
                        _com_talk.shop = obj.dialog_tb.shop
                        _com_talk.nickname = obj.dialog_tb.customer
                        _com_talk.goods_name = _rt_com_talk[1].replace("型号", "")
                        _com_talk.compensation = _rt_com_talk[2].replace('差价', '').replace(' ', '')
                        _com_talk.name = _rt_com_talk[3].replace('姓名', '').replace(' ', '')
                        _com_talk.alipay_id = _rt_com_talk[4].replace('支付宝', '').replace(' ', '')
                        _com_talk.order_id = _rt_com_talk[5].replace('订单号', '').replace(' ', '')
                        formula = _rt_com_talk[6]
                        _com_talk.order_category = _rt_com_talk[7]

                        _q_goods_name = MachineInfo.objects.filter(goods_name=_com_talk.goods_name)
                        if not _q_goods_name.exists():
                            result["false"] += 1
                            obj.mistake_tag = 3
                            obj.category = 2
                            obj.save()
                            continue
                        try:
                            _com_talk.compensation = float(_com_talk.compensation)

                        except Exception as e:
                            result["false"] += 1
                            result["error"].append(e)
                            obj.mistake_tag = 4
                            obj.category = 2
                            obj.save()
                            continue
                        if not _com_talk.name:
                            result["false"] += 1
                            obj.mistake_tag = 5
                            obj.category = 2
                            obj.save()
                            continue
                        if not _com_talk.alipay_id:
                            result["false"] += 1
                            obj.mistake_tag = 6
                            obj.category = 2
                            obj.save()
                            continue
                        if not re.match(r'^[0-9]+$', _com_talk.order_id):
                            result["false"] += 1
                            obj.mistake_tag = 7
                            obj.category = 2
                            obj.save()
                            continue
                        if _com_talk.order_category not in ['1', '3']:
                            result["false"] += 1
                            obj.mistake_tag = 11
                            obj.category = 2
                            obj.save()
                            continue
                        if re.match(r'^\d+-+\d+=\d+$', formula):

                            elements = str(formula).split("-", 1)
                            _com_talk.actual_receipts = float(elements[0])

                            transition = str(elements[1]).split("=")
                            _com_talk.receivable = float(transition[0])
                            _com_talk.checking = float(transition[1])
                            if _com_talk.actual_receipts - _com_talk.receivable != _com_talk.checking:
                                result["false"] += 1
                                obj.mistake_tag = 9
                                obj.category = 2
                                obj.save()
                                continue
                            if _com_talk.checking != _com_talk.compensation:
                                result["false"] += 1
                                obj.mistake_tag = 10
                                obj.category = 2
                                obj.save()
                                continue
                        else:
                            result["false"] += 1
                            obj.mistake_tag = 8
                            obj.category = 2
                            obj.save()
                            continue

                        try:
                            _com_talk.creator = self.request.user.username
                            _com_talk.save()
                            _com_dia_list.ori_order = _com_talk
                            _com_dia_list.dialog_order = obj
                            _com_dia_list.creator = self.request.user.username
                            _com_dia_list.save()
                            obj.category = 2
                            result["successful"] += 1
                        except Exception as e:
                            result["false"] += 1
                            result["error"].append(e)
                            obj.mistake_tag = 1
                            obj.category = 2
                            obj.save()
                            continue



                    else:
                        result['false'] += 1
                        result['error'].append("对话的格式不对，导致无法提取")
                        obj.category = 2
                        obj.mistake_tag = 1
                        obj.save()
                        continue
                obj.extract_tag = 1
                obj.save()
            self.message_user(result)
            self.message_user("提交 %(count)d %(items)s。" % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 官方商城对话明细提取订单
class ExtractODOWAction(BaseActionView):
    action_name = "extract_dialog_content_ow"
    description = "提取选中的对话"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        _rt_talk_title_new = ['order_category', 'servicer', 'goods', 'order_id', 'cs_information']
        _rt_talk_title_total = ['order_category', 'servicer', 'goods', 'order_id', 'cs_information',
                                'm_sn', 'broken_part', 'description']
        result = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            queryset.filter(d_status=1).update(extract_tag=1)
            queryset = queryset.filter(d_status=0)
            for obj in queryset:
                if OrderOWList.objects.filter(talk_ow=obj).exists():
                    result["discard"] += 1
                    obj.mistake_tag = 2
                    obj.save()
                    continue
                else:
                    order_list_ow = OrderOWList()
                _check_talk_data = re.findall(r'(·客服.*{.*}[\s\S]*?.*})', str(obj.content), re.DOTALL)
                if _check_talk_data:
                    _rt_talk = GiftInTalkInfo()
                    _rt_talk.platform = 3
                    _rt_talk_data = re.findall(r'{((?:.|\n)*?)}', str(obj.content), re.DOTALL)

                    if len(_rt_talk_data) == 5:
                        _rt_talk.platform = 3
                        _rt_talk_dic = dict(zip(_rt_talk_title_new, _rt_talk_data))
                        for k, v in _rt_talk_dic.items():
                            if hasattr(_rt_talk, k):
                                setattr(_rt_talk, k, v)
                    elif len(_rt_talk_data) == 8:
                        _rt_talk.platform = 3
                        _rt_talk_dic = dict(zip(_rt_talk_title_total, _rt_talk_data))
                        for k, v in _rt_talk_dic.items():
                            if hasattr(_rt_talk, k):
                                setattr(_rt_talk, k, v)

                    else:
                        result['false'] += 1
                        result['error'].append("%s 对话的格式不对，导致无法提取" % _rt_talk_data[1])
                        obj.category = 1
                        obj.mistake_tag = 1
                        obj.save()
                        continue
                    try:
                        _rt_talk.shop = obj.dialog_ow.shop
                        _rt_talk.creator = self.request.user.username
                        _rt_talk.nickname = '客户ID%s' % obj.dialog_ow.customer
                        _rt_talk.save()
                        order_list_ow.gift_order = _rt_talk
                        order_list_ow.talk_ow = obj
                        order_list_ow.creator = self.request.user.username
                        order_list_ow.save()
                        obj.category = 1
                        result["successful"] += 1
                    except Exception as e:
                        result["false"] += 1
                        result["error"].append(e)
                        obj.mistake_tag = 1
                        obj.category = 1
                        obj.save()
                        continue
                obj.extract_tag = 1
                obj.save()
            self.message_user(result)
            self.message_user("提交 %(count)d %(items)s。" % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 放弃对话明细订单内容提取订单
class PassODJDAction(BaseActionView):
    action_name = "pass_dialog_content"
    description = "丢弃选中的对话"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:

            self.log('change',
                     '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
            queryset.update(extract_tag=1)
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                          'success')
        return None


# 淘宝对话明细内联
class ODTBInfoInline(object):

    model = OriDetailTB
    exclude = ["is_delete", 'creator', 'update_time', 'create_time']
    extra = 0
    style = 'table'


# 淘宝对话查询界面
class OriDialogTBAdmin(object):
    list_display = ['shop', 'customer', 'start_time', 'end_time', 'min', 'dialog_tag']
    list_filter = ['shop', 'customer', 'start_time', 'end_time', 'min', 'dialog_tag__name', 'creator']
    search_fields = ['customer']
    inlines = [ODTBInfoInline]
    import_data = True

    def post(self, request, *args, **kwargs):

        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(file)
            self.message_user('结果提示：%s' % result)
        return super(OriDialogTBAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, _file):

        ALLOWED_EXTENSIONS = ['txt']
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        if '.' in _file.name and _file.name.rsplit('.')[-1] in ALLOWED_EXTENSIONS:
            start_tag = 0

            dialog_contents = []
            dialog_content = []
            i = 0
            while True:
                i += 1
                try:
                    data_line = _file.readline().decode('gbk')
                except Exception as e:
                    continue
                end_tag = re.findall(r'^\s{31}(.*)\s{29}', data_line)
                if end_tag:
                    if str(end_tag[0]).strip() == '群聊':
                        break
                if not data_line:
                    break
                if i == 1:
                    try:
                        info = str(data_line).strip().replace('\n', '').replace('\r', '')
                        if ":" in info:
                            info = info.split(":")[0]
                        shop = info
                        if not shop:
                            report_dic['error'].append('请使用源表进行导入，不要对表格进行处理。')
                            break
                        continue
                    except Exception as e:
                        report_dic['error'].append('请使用源表进行导入，不要对表格进行处理。')
                        break

                customer = re.findall(r'^-{28}(.*)-{28}', data_line)
                if customer:
                    if dialog_content:
                        dialog_contents.append(dialog_content)
                        dialog_content = []
                    if dialog_contents:
                        _q_dialog = OriDialogTB.objects.filter(shop=shop, customer=current_customer)
                        if _q_dialog.exists():
                            dialog_order = _q_dialog[0]
                            end_time = datetime.datetime.strptime(str(dialog_contents[-1][1]), '%Y-%m-%d %H:%M:%S')
                            if dialog_order.end_time == end_time:
                                report_dic['discard'] += 1
                                current_customer = customer[0]
                                dialog_contents.clear()
                                dialog_content.clear()
                                continue
                            dialog_order.end_time = end_time
                            dialog_order.min += 1
                        else:
                            dialog_order = OriDialogTB()
                            dialog_order.customer = current_customer
                            dialog_order.shop = shop
                            start_time = datetime.datetime.strptime(str(dialog_contents[0][1]), '%Y-%m-%d %H:%M:%S')
                            end_time = datetime.datetime.strptime(str(dialog_contents[-1][1]), '%Y-%m-%d %H:%M:%S')
                            dialog_order.start_time = start_time
                            dialog_order.end_time = end_time
                            dialog_order.min = 1
                        try:
                            dialog_order.creator = self.request.user.username
                            dialog_order.save()
                            report_dic['successful'] += 1
                        except Exception as e:
                            report_dic['error'].append(e)
                            report_dic['false'] += 1
                            dialog_contents.clear()
                            dialog_content.clear()
                            current_customer = customer[0]
                            continue
                        previous_time = datetime.datetime.strptime(str(dialog_contents[0][1]), '%Y-%m-%d %H:%M:%S')
                        for dialog_content in dialog_contents:
                            _q_dialog_detial = OriDetailTB.objects.filter(sayer=dialog_content[0],
                                                                          time=datetime.datetime.strptime
                                                                          (str(dialog_content[1]), '%Y-%m-%d %H:%M:%S'))
                            if _q_dialog_detial.exists():
                                report_dic['discard'] += 1
                                continue
                            dialog_detial = OriDetailTB()
                            dialog_detial.dialog_tb = dialog_order
                            dialog_detial.sayer = dialog_content[0]
                            dialog_detial.time = datetime.datetime.strptime(str(dialog_content[1]), '%Y-%m-%d %H:%M:%S')
                            dialog_detial.content = dialog_content[2]
                            d_value = (dialog_detial.time - previous_time).seconds
                            dialog_detial.interval = d_value
                            previous_time = datetime.datetime.strptime(str(dialog_content[1]), '%Y-%m-%d %H:%M:%S')
                            if dialog_content[0] == current_customer:
                                dialog_detial.d_status = 1
                            else:
                                dialog_detial.d_status = 0
                            try:
                                dialog_detial.creator = self.request.user.username
                                dialog_detial.content = emoji.demojize(str(dialog_detial.content))
                                dialog_detial.save()
                            except Exception as e:
                                report_dic['error'].append(e)
                        dialog_contents.clear()
                        dialog_content.clear()
                        current_customer = customer[0]
                    else:
                        current_customer = customer[0]
                    start_tag = 1
                    continue
                if start_tag:
                    dialog = re.findall(r'(.*)(\(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\):  )(.*)', str(data_line))

                    if dialog:
                        if len(dialog[0]) == 3:
                            if dialog_content:
                                dialog_contents.append(dialog_content)
                                dialog_content = []
                            dialog_content.append(dialog[0][0])
                            dialog_content.append(str(dialog[0][1]).replace('(', '').replace('):  ', ''))
                            dialog_content.append(str(dialog[0][2]))
                    else:
                        try:
                            dialog_content[2] = '%s%s' % (dialog_content[2], str(data_line))

                        except Exception as e:
                            report_dic['error'].append(e)

                if re.match(r'^={64}', str(data_line)):
                    if dialog_content:
                        dialog_contents.append(dialog_content)
                        dialog_content = []
                    if dialog_contents:

                        _q_dialog = OriDialogTB.objects.filter(shop=shop, customer=current_customer)
                        if _q_dialog.exists():
                            dialog_order = _q_dialog[0]
                            end_time = datetime.datetime.strptime(str(dialog_contents[-1][1]), '%Y-%m-%d %H:%M:%S')
                            if dialog_order.end_time >= end_time:
                                report_dic['discard'] += 1
                                continue
                            dialog_order.end_time = end_time
                            dialog_order.min += 1
                        else:
                            dialog_order = OriDialogTB()
                            dialog_order.customer = current_customer
                            dialog_order.shop = shop
                            start_time = datetime.datetime.strptime(str(dialog_contents[0][1]), '%Y-%m-%d %H:%M:%S')
                            end_time = datetime.datetime.strptime(str(dialog_contents[-1][1]), '%Y-%m-%d %H:%M:%S')
                            dialog_order.start_time = start_time
                            dialog_order.end_time = end_time
                            dialog_order.min = 1
                        try:
                            dialog_order.creator = self.request.user.username
                            dialog_order.save()
                            report_dic['successful'] += 1
                        except Exception as e:
                            report_dic['error'].append(e)
                            report_dic['false'] += 1
                            continue
                        previous_time = datetime.datetime.strptime(str(dialog_contents[0][1]), '%Y-%m-%d %H:%M:%S')
                        for dialog_content in dialog_contents:
                            _q_dialog_detial = OriDetailTB.objects.filter(sayer=dialog_content[0],
                                                                          time=datetime.datetime.strptime
                                                                          (str(dialog_content[1]), '%Y-%m-%d %H:%M:%S'))
                            if _q_dialog_detial.exists():
                                report_dic['discard'] += 1
                                continue
                            dialog_detial = OriDetailTB()
                            dialog_detial.dialog_tb = dialog_order
                            dialog_detial.sayer = dialog_content[0]
                            dialog_detial.time = datetime.datetime.strptime(str(dialog_content[1]), '%Y-%m-%d %H:%M:%S')
                            dialog_detial.content = dialog_content[2]
                            d_value = (dialog_detial.time - previous_time).seconds
                            dialog_detial.interval = d_value
                            previous_time = datetime.datetime.strptime(str(dialog_content[1]), '%Y-%m-%d %H:%M:%S')
                            if dialog_content[0] == current_customer:
                                dialog_detial.d_status = 1
                            else:
                                dialog_detial.d_status = 0
                            try:
                                dialog_detial.creator = self.request.user.username
                                dialog_detial.content = emoji.demojize(str(dialog_detial.content))
                                dialog_detial.save()
                            except Exception as e:
                                report_dic['error'].append(e)
                        start_tag = 0
            return report_dic


        else:
            error = "只支持文本文件格式！"
            report_dic["error"].append(error)
            return report_dic


# 淘宝过滤敏感字界面
class CheckODTBAdmin(object):
    list_display = ['dialog_tb', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'sensitive_tag', 'order_status']
    list_filter = ['dialog_tb__customer', 'index_num', 'extract_tag', 'sensitive_tag', 'sayer', 'd_status', 'time',
                   'interval', 'content', 'mistake_tag']
    search_fields = ['dialog_tb__customer']
    actions = [CheckAction]

    def queryset(self):
        queryset = super(CheckODTBAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, sensitive_tag=0)
        return queryset


# 淘宝异常对话界面
class ExceptionODTBAdmin(object):
        list_display = ['dialog_tb', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'sensitive_tag',
                        'order_status']
        list_filter = ['dialog_tb__customer', 'index_num', 'extract_tag', 'sensitive_tag', 'sayer', 'd_status', 'time',
                       'interval', 'content']
        search_fields = ['dialog_tb__customer']

        def queryset(self):
            queryset = super(ExceptionODTBAdmin, self).queryset()
            queryset = queryset.filter(is_delete=0, sensitive_tag=1, index_num__gt=0)
            return queryset


# 淘宝对话明细订单提取界面
class ExtractODTBAdmin(object):
    list_display = ['dialog_tb', 'mistake_tag', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num',
                    'sensitive_tag', 'order_status', 'create_time']
    list_filter = ['dialog_tb__customer', 'mistake_tag', 'index_num', 'extract_tag', 'sensitive_tag', 'sayer', 'd_status',
                   'time', 'interval', 'content', 'creator']
    search_fields = ['dialog_tb__customer']
    readonly_fields = ['dialog_tb', 'mistake_tag', 'sayer', 'd_status', 'time', 'interval', 'index_num', 'sensitive_tag',
                       'order_status', 'creator', 'extract_tag']
    list_editable = ['content']
    actions = [ExtractODTBAction, PassODJDAction]

    def queryset(self):
        queryset = super(ExtractODTBAdmin, self).queryset()
        queryset = queryset.filter(extract_tag=0)
        return queryset


# 淘宝对话明细订单提取界面
class MyExtractODTBAdmin(object):
    list_display = ['dialog_tb', 'mistake_tag', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num',
                    'sensitive_tag', 'order_status', 'create_time']
    list_filter = ['dialog_tb__customer', 'index_num', 'extract_tag', 'sensitive_tag', 'sayer', 'd_status', 'time',
                   'interval', 'content']
    search_fields = ['dialog_tb__customer']
    readonly_fields = ['dialog_tb', 'mistake_tag', 'sayer', 'd_status', 'time', 'interval', 'index_num', 'sensitive_tag',
                       'order_status', 'creator', 'extract_tag']
    list_editable = ['content']
    actions = [ExtractODTBAction, PassODJDAction]

    def queryset(self):
        queryset = super(MyExtractODTBAdmin, self).queryset()
        queryset = queryset.filter(extract_tag=0, creator=self.request.user.username)
        return queryset


# 淘宝对话明细查询界面
class OriDetailTBAdmin(object):
    list_display = ['dialog_tb', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'extract_tag',
                    'sensitive_tag', 'order_status', 'create_time']
    list_filter = ['dialog_tb__customer', 'mistake_tag', 'category', 'create_time', 'index_num', 'extract_tag', 'sensitive_tag', 'sayer', 'd_status',
                   'time', 'interval', 'content', 'creator']
    search_fields = ['dialog_tb__customer']
    readonly_fields = ['dialog_tb', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'extract_tag',
                       'sensitive_tag', 'order_status', 'creator', 'is_delete', 'mistake_tag', 'category',]
    actions = [ResetODJDExtract, ResetODJDSensitive]


# 京东内联明细
class ODJDInfoInline(object):

    model = OriDetailJD
    exclude = ["is_delete", 'creator', 'update_time', 'create_time']
    extra = 0
    style = 'table'


# 京东对话查询界面
class OriDialogJDAdmin(object):
    list_display = ['shop', 'customer', 'start_time', 'end_time', 'min', 'dialog_tag', 'create_time']
    list_filter = ['shop', 'customer', 'start_time', 'end_time', 'min', 'dialog_tag__name', 'creator']
    search_fields = ['customer']
    inlines = [ODJDInfoInline,]
    import_data = True

    def post(self, request, *args, **kwargs):

        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(file)
            self.message_user('结果提示：%s' % result)
        return super(OriDialogJDAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, _file):

        ALLOWED_EXTENSIONS = ['log']
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        if '.' in _file.name and _file.name.rsplit('.')[-1] in ALLOWED_EXTENSIONS:
            start_tag = 0

            dialog_contents = []
            dialog_content = []
            i = 0
            content = ''
            shop = ''
            _q_servicer_list = ServicerInfo.objects.filter(platform='京东').values_list('name', flat=True)
            _q_robot_list = ServicerInfo.objects.filter(category=0, platform='京东').values_list('name', flat=True)
            robot_list = list(_q_robot_list)
            servicer_list = list(_q_servicer_list)
            while True:
                i += 1
                data_line = _file.readline().decode('utf8')
                if not data_line:
                    break

                if re.match(r'^\/\*{17}以下为一通会话', data_line):
                    start_tag = 1
                    continue
                if re.match(r'^\/\*{17}会话结束', data_line):
                    if dialog_contents:
                        try:
                            rank = 0
                            while True:
                                customer = str(dialog_contents[rank][0]).replace(' ', '')
                                if customer in servicer_list:
                                    rank += 1
                                    continue
                                else:
                                    dialog_content.append(content)
                                    dialog_contents.append(dialog_content)
                                    dialog_content = []
                                    content = ''
                                    break
                        except Exception as e:
                            report_dic['error'].append('客户无回应留言丢弃。 %s' % e)
                            dialog_contents.clear()
                            dialog_content.clear()
                            content = ''
                            continue
                    else:
                        report_dic['error'].append('对话主体就一句话，或者文件格式出现错误！')
                        dialog_contents.clear()
                        dialog_content.clear()
                        content = ''
                        continue
                    if not shop:
                        dialog_contents.clear()
                        dialog_content.clear()
                        report_dic['error'].append('店铺出现错误，检查源文件！')
                        break

                    _q_dialog = OriDialogJD.objects.filter(shop=shop, customer=customer)
                    if _q_dialog.exists():
                        dialog_order = _q_dialog[0]
                        try:
                            end_time = datetime.datetime.strptime(str(dialog_contents[-1][1]), '%Y-%m-%d %H:%M:%S')
                        except Exception as e:
                            report_dic['error'].append(e)
                            continue
                        if dialog_order.end_time == end_time:
                            report_dic['discard'] += 1
                            dialog_contents.clear()
                            dialog_content.clear()
                            content = ''
                            start_tag = 0
                            continue
                        dialog_order.end_time = end_time
                        dialog_order.min += 1
                    else:
                        dialog_order = OriDialogJD()
                        dialog_order.customer = customer
                        dialog_order.shop = shop
                        try:
                            start_time = datetime.datetime.strptime(str(dialog_contents[0][1]), '%Y-%m-%d %H:%M:%S')
                            end_time = datetime.datetime.strptime(str(dialog_contents[-1][1]), '%Y-%m-%d %H:%M:%S')
                        except Exception as e:
                            report_dic['error'].append(e)
                            continue
                        dialog_order.start_time = start_time
                        dialog_order.end_time = end_time
                        dialog_order.min = 1
                    try:
                        dialog_order.creator = self.request.user.username
                        dialog_order.save()
                        report_dic['successful'] += 1
                    except Exception as e:
                        report_dic['error'].append(e)
                        report_dic['false'] += 1
                        dialog_contents.clear()
                        dialog_content.clear()
                        content = ''
                        start_tag = 0
                        continue
                    previous_time = datetime.datetime.strptime(str(dialog_contents[0][1]), '%Y-%m-%d %H:%M:%S')
                    for dialog_content in dialog_contents:
                        # 屏蔽机器人对话
                        servicer = str(dialog_content[0])
                        if servicer in robot_list:
                            continue
                        _q_dialog_detial = OriDetailJD.objects.filter(sayer=dialog_content[0],
                                                                      time=datetime.datetime.strptime
                                                                      (str(dialog_content[1]), '%Y-%m-%d %H:%M:%S'))
                        if _q_dialog_detial.exists():
                            dialog_detial = _q_dialog_detial[0]
                            dialog_detial.content = '%s%s' % (dialog_detial.content, dialog_content[2])
                            dialog_detial.content = emoji.demojize(str(dialog_detial.content))
                            dialog_detial.save()
                            continue
                        dialog_detial = OriDetailJD()
                        dialog_detial.dialog_jd = dialog_order
                        dialog_detial.sayer = dialog_content[0]
                        try:
                            dialog_detial.time = datetime.datetime.strptime(str(dialog_content[1]), '%Y-%m-%d %H:%M:%S')
                        except Exception as e:
                            report_dic['error'].append(e)
                            continue
                        dialog_detial.content = emoji.demojize(str(dialog_content[2]))
                        d_value = (dialog_detial.time - previous_time).seconds
                        dialog_detial.interval = d_value
                        previous_time = dialog_detial.time
                        current_sayer = str(dialog_content[0]).replace(' ', '')
                        if current_sayer in servicer_list:
                            dialog_detial.d_status = 0
                        else:
                            dialog_detial.d_status = 1
                        try:
                            dialog_detial.creator = self.request.user.username
                            dialog_detial.save()
                        except Exception as e:
                            report_dic['error'].append(e)
                    dialog_contents.clear()
                    dialog_content.clear()
                    content = ''
                    start_tag = 0
                    continue
                if start_tag:
                    dialog = re.findall(r'(.*)(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', str(data_line))
                    info = str(data_line).split(' ')
                    num = len(info)
                    if dialog and num == 3:
                        if content:
                            dialog_content.append(content)
                            if len(dialog_content) == 3:
                                dialog_contents.append(dialog_content)
                            dialog_content = []
                        dialog_content.append(dialog[0][0])
                        dialog_content.append(dialog[0][1])
                        if i < 10:
                            if re.match(r'^小狗.*', dialog[0][0]):
                                _shop_word = dialog[0][0][:4]
                                _shop_list = {
                                    '小狗旗舰': '小狗京东商城店铺FBP',
                                    '小狗自营': '小狗京东自营',
                                }
                                shop = _shop_list.get(_shop_word, None)
                        content = ''
                    else:
                        content = '%s%s' % (content, str(data_line))
            return report_dic

        else:
            error = "只支持文本文件格式！"
            report_dic["error"].append(error)
            return report_dic


# 过滤敏感字
class CheckODJDAdmin(object):
    list_display = ['dialog_jd', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'sensitive_tag', 'order_status', 'create_time']
    list_filter = ['dialog_jd__customer', 'index_num', 'extract_tag', 'sensitive_tag', 'sayer', 'd_status', 'time',
                   'interval', 'content', 'mistake_tag']
    search_fields = ['dialog_jd__customer']
    actions = [CheckAction]

    def queryset(self):
        queryset = super(CheckODJDAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, sensitive_tag=0)
        return queryset


# 异常对话界面
class ExceptionODJDAdmin(object):
    list_display = ['dialog_jd', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'sensitive_tag',
                    'order_status', 'create_time']
    list_filter = ['dialog_jd__customer', 'index_num', 'extract_tag', 'sensitive_tag', 'sayer', 'd_status', 'time',
                   'interval', 'content', 'update_time']
    search_fields = ['dialog_jd__customer']

    def queryset(self):
        queryset = super(ExceptionODJDAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, sensitive_tag=1, index_num__gt=0)
        return queryset


# 订单提取界面
class ExtractODJDAdmin(object):
    list_display = ['dialog_jd', 'mistake_tag', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'sensitive_tag', 'order_status']
    list_filter = ['dialog_jd__customer', 'index_num', 'extract_tag', 'sensitive_tag', 'sayer', 'd_status', 'time',
                   'interval', 'content', 'creator']
    search_fields = ['dialog_jd__customer']
    readonly_fields = ['dialog_jd', 'mistake_tag', 'sayer', 'd_status', 'time', 'interval', 'index_num', 'sensitive_tag', 'order_status', 'creator', 'extract_tag']
    list_editable = ['content']
    actions = [ExtractODJDAction, PassODJDAction]

    def queryset(self):
        queryset = super(ExtractODJDAdmin, self).queryset()
        queryset = queryset.filter(extract_tag=0)
        return queryset


# 京东对话明细
class OriDetailJDAdmin(object):
    list_display = ['dialog_jd', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'extract_tag',
                    'sensitive_tag', 'order_status', 'create_time']
    list_filter = ['dialog_jd__customer', 'mistake_tag', 'category', 'index_num', 'extract_tag', 'sensitive_tag', 'sayer',
                   'd_status', 'time', 'interval', 'content', 'creator']
    search_fields = ['dialog_jd__customer']
    readonly_fields = ['dialog_jd', 'sayer', 'category', 'create_time', 'd_status', 'time', 'interval', 'content',
                       'index_num', 'extract_tag', 'sensitive_tag', 'order_status', 'creator', 'is_delete', 'mistake_tag']
    actions = [ResetODJDExtract, ResetODJDSensitive]





class OriDialogOWAdmin(object):
    list_display = ['shop', 'customer', 'start_time', 'end_time', 'min', 'dialog_tag', 'order_status']
    list_filter = ['customer', 'creator', 'start_time', 'end_time', 'min', 'dialog_tag', 'order_status',
                   'creator', 'create_time']
    search_fields = ['customer']

    form_layout = [
        Fieldset('客户信息',
                 Row('customer', 'shop',),
                 Row('start_time', 'end_time', 'min',),),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]
    readonly_fields = ['is_delete', 'shop', 'customer', 'start_time', 'min', 'dialog_tag', 'order_status',
                       'creator', 'create_time', 'update_time']


    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {"客户": "customer", "对话开始时间": "start_time", "对话内容": "content", "对话ID": "dialog_id"}
    import_data = True

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('导入结果 %s' % result, 'success')
        return super(OriDialogOWAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0)

            FILTER_FIELDS = ['客户', '对话开始时间', '对话内容', '对话ID']

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
            _ret_verify_field = OriDialogOW.verify_mandatory(columns_key)
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
            df = pd.read_csv(_file, encoding="gb18030", chunksize=300)

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
                _ret_verify_field = OriDialogOW.verify_mandatory(columns_key)
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

        shop = '小狗官方商城'

        # 开始导入数据
        i = 1
        for row in resource:
            content = str(row["content"])
            customer = str(row["customer"])
            dialog_id = str(row['dialog_id'])
            if not dialog_id:
                report_dic['discard'] += 1
                continue
            _q_dowid = DOWID.objects.filter(dialog_id=dialog_id)
            if _q_dowid.exists():
                report_dic['repeated'] += 1
                continue
            else:
                dialog_id_order = DOWID()
                dialog_id_order.dialog_id = dialog_id
            try:
                dialog_id_order.save()
            except Exception as e:
                report_dic['false'] += 1
                report_dic['error'].append(e)
                continue

            if customer == "小程序用户":
                while True:
                    serial_number = str(datetime.datetime.now())[:10]
                    postfix = str(int(serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", ""))) + str(i)
                    i += 1
                    customer = customer + postfix
                    _q_dialog = OriDialogOW.objects.filter(shop=shop, customer=customer)
                    if _q_dialog.exists():
                        continue
                    else:
                        break

            content_list = content.split('\r\n')
            content_dic = {'content_text': '', 'sayer': ''}
            dialog_contents = []
            tag = 0
            for words in content_list:
                words = words.replace('\r', '')
                if re.match(r'----\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2}----', words):
                    tag = 0
                elif re.match(r'[\S]+\s\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2}', words):
                    tag = 1
                    if content_dic['sayer']:
                        dialog_contents.append(content_dic)
                    content_dic = {'content_text': '', 'sayer': ''}
                    sayer_info = words.split(' ', 1)
                    content_dic['sayer'] = str(sayer_info[0]).replace('/r', '').replace(' ', '').replace('/n', '')
                    content_dic['time'] = str(sayer_info[1]).replace('/r', '').replace('/n', '')
                else:
                    if tag == 1:
                        content_dic['content_text'] = content_dic['content_text'] + words
            if content_dic['sayer']:
                dialog_contents.append(content_dic)
            if not dialog_contents:
                continue
            start_time = dialog_contents[0]['time']
            _q_dialog = OriDialogOW.objects.filter(shop=shop, customer=customer)
            if _q_dialog.exists():
                dialog_order = _q_dialog[0]
                end_time = datetime.datetime.strptime(str(dialog_contents[-1]['time']), '%Y/%m/%d %H:%M:%S')
                dialog_order.end_time = end_time
                dialog_order.min += 1
            else:
                dialog_order = OriDialogOW()
                dialog_order.customer = customer
                dialog_order.shop = shop
                start_time = datetime.datetime.strptime(str(start_time), '%Y/%m/%d %H:%M:%S')
                end_time = datetime.datetime.strptime(str(dialog_contents[-1]['time']), '%Y/%m/%d %H:%M:%S')
                dialog_order.start_time = start_time
                dialog_order.end_time = end_time
                dialog_order.min = 1
            try:
                dialog_order.creator = request.user.username
                dialog_order.save()
                report_dic['successful'] += 1
            except Exception as e:
                report_dic['error'].append(e)
                report_dic['false'] += 1
                continue
            previous_time = datetime.datetime.strptime(str(dialog_contents[0]['time']), '%Y/%m/%d %H:%M:%S')
            for dialog_content in dialog_contents:
                sayer = dialog_content['sayer']
                time = dialog_content['time']
                content_text = dialog_content['content_text']
                if sayer == '客户':
                    sayer = customer
                _q_dialog_detial = OriDetailOW.objects.filter(sayer=sayer,
                                                              time=datetime.datetime.strptime
                                                              (str(time), '%Y/%m/%d %H:%M:%S'))
                if _q_dialog_detial.exists():
                    report_dic['discard'] += 1
                    continue
                dialog_detial = OriDetailOW()
                dialog_detial.dialog_ow = dialog_order
                dialog_detial.sayer = sayer
                dialog_detial.time = datetime.datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S')
                dialog_detial.content = content_text
                d_value = (dialog_detial.time - previous_time).seconds
                dialog_detial.interval = d_value
                previous_time = datetime.datetime.strptime(str(dialog_content['time']), '%Y/%m/%d %H:%M:%S')
                if sayer == customer:
                    dialog_detial.d_status = 1
                else:
                    dialog_detial.d_status = 0
                try:
                    dialog_detial.creator = request.user.username
                    dialog_detial.content = emoji.demojize(str(dialog_detial.content))
                    dialog_detial.save()
                except Exception as e:
                    report_dic['error'].append(e)

        return report_dic

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.servicer = request.user.username
        obj.order_status = 3
        obj.save()
        super().save_models()


class OriDetailOWAdmin(object):
    list_display = ['dialog_ow', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'category', 'extract_tag',
                    'sensitive_tag', 'order_status', 'mistake_tag', 'create_time']
    list_filter = ['dialog_ow__customer', 'dialog_ow__creator', 'dialog_ow__start_time', 'dialog_ow__end_time', 'sayer',
                   'd_status', 'interval', 'creator', 'create_time', 'content', 'category']
    search_fields = ['dialog_ow__customer',]
    actions = [ResetODJDExtract]
    form_layout = [
        Fieldset('客户信息',
                 Row('sayer', 'd_status', ),
                 Row('time', 'interval', 'category', ),
                 'content',),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]
    readonly_fields = ['dialog_ow', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'category',
                       'extract_tag', 'sensitive_tag', 'order_status', 'mistake_tag']


class CheckODOWAdmin(object):
    pass


class ExtractODOWadmin(object):
    list_display = ['dialog_ow', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'category', 'extract_tag',
                    'sensitive_tag', 'order_status', 'mistake_tag', 'create_time']
    list_filter = ['dialog_ow__customer', 'dialog_ow__creator', 'dialog_ow__start_time', 'dialog_ow__end_time', 'sayer',
                   'd_status', 'interval', 'creator', 'create_time', 'content',]
    search_fields = ['dialog_ow__customer',]
    list_editable = ['content']
    form_layout = [
        Fieldset('客户信息',
                 Row('sayer', 'd_status', ),
                 Row('time', 'interval', 'category', ),
                 'content', ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]
    readonly_fields = ['dialog_ow', 'sayer', 'd_status', 'time', 'interval', 'index_num', 'category',
                       'extract_tag', 'sensitive_tag', 'order_status', 'mistake_tag']
    actions = [ExtractODOWAction, PassODJDAction]

    def queryset(self):
        queryset = super(ExtractODOWadmin, self).queryset()
        queryset = queryset.filter(extract_tag=0)
        return queryset


class MyExtractODOWAdmin(object):
    list_display = ['dialog_ow', 'sayer', 'd_status', 'time', 'interval', 'content', 'index_num', 'category', 'extract_tag',
                    'sensitive_tag', 'order_status', 'mistake_tag', 'create_time']
    list_filter = ['dialog_ow__customer', 'dialog_ow__creator', 'dialog_ow__start_time', 'dialog_ow__end_time', 'sayer',
                   'd_status', 'interval', 'creator', 'create_time', 'content',]
    search_fields = ['dialog_ow__customer',]
    list_editable = ['content']
    form_layout = [
        Fieldset('客户信息',
                 Row('sayer', 'd_status', ),
                 Row('time', 'interval', 'category', ),
                 'content', ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]
    readonly_fields = ['dialog_ow', 'sayer', 'd_status', 'time', 'interval', 'index_num', 'category',
                       'extract_tag', 'sensitive_tag', 'order_status', 'mistake_tag']
    actions = [ExtractODOWAction, PassODJDAction]

    def queryset(self):
        queryset = super(MyExtractODOWAdmin, self).queryset()
        queryset = queryset.filter(extract_tag=0, creator=self.request.user.username)
        return queryset


class ExceptionODOWAdmin(object):
    pass


class DOWIDAdmin(object):
    list_display = ['dialog_id']
    list_filter = ['dialog_id', 'create_time', 'creator']
    search_fields = ['dialog_id', ]


xadmin.site.register(DialogTag, DialogTagAdmin)
xadmin.site.register(SensitiveInfo, SensitiveInfoAdmin)
xadmin.site.register(ServicerInfo, ServicerInfoAdmin)
xadmin.site.register(OriDialogTB, OriDialogTBAdmin)
xadmin.site.register(OriDetailTB, OriDetailTBAdmin)

xadmin.site.register(CheckODTB, CheckODTBAdmin)
xadmin.site.register(ExceptionODTB, ExceptionODTBAdmin)
xadmin.site.register(ExtractODTB, ExtractODTBAdmin)
xadmin.site.register(MyExtractODTB, MyExtractODTBAdmin)

xadmin.site.register(OriDialogJD, OriDialogJDAdmin)
xadmin.site.register(CheckODJD, CheckODJDAdmin)
xadmin.site.register(ExceptionODJD, ExceptionODJDAdmin)
xadmin.site.register(ExtractODJD, ExtractODJDAdmin)
xadmin.site.register(OriDetailJD, OriDetailJDAdmin)

xadmin.site.register(OriDialogOW, OriDialogOWAdmin)
xadmin.site.register(OriDetailOW, OriDetailOWAdmin)
xadmin.site.register(CheckODOW, CheckODOWAdmin)
xadmin.site.register(ExtractODOW, ExtractODOWadmin)
xadmin.site.register(MyExtractODOW, MyExtractODOWAdmin)
xadmin.site.register(ExceptionODOW, ExceptionODOWAdmin)

xadmin.site.register(DOWID, DOWIDAdmin)


