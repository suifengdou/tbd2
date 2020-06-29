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
from xadmin.layout import Fieldset
import emoji

from .models import DialogTag, OriDialogTB, OriDetailTB, OriDialogJD, OriDetailJD, ServicerInfo, MyExtractODTB
from .models import SensitiveInfo, CheckODJD, ExtractODJD, ExceptionODJD, CheckODTB, ExtractODTB, ExceptionODTB
from apps.base.shop.models import ShopInfo
from apps.assistants.giftintalk.models import GiftInTalkInfo, OrderTBList, OrderJDList

ACTION_CHECKBOX_NAME = '_selected_action'


# 对话标签界面
class DialogTagAdmin(object):
    list_display = ['name', 'category', 'order_status']


# 客服信息界面
class ServicerInfoAdmin(object):
    list_display =['name', 'platform', 'username', 'category']


# 敏感字管理界面
class SensitiveInfoAdmin(object):
    list_display = ['words', 'index', 'category', 'order_status']
    search_fields = ['words']
    list_filter = ['index', 'category', 'order_status']

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
            '指数': 'index',
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

    def add(self, sensitive):
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
                last_level[last_char] = {self.delimit: sensitive.index}
                break
        if i == len(chars) - 1:
            level[self.delimit] = sensitive.index

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
                        obj.index += level[char][self.delimit]
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
        result = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            queryset.filter(status=1).update(extract_tag=1)
            queryset = queryset.filter(status=0)
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

                    else:
                        result['false'] += 1
                        result['error'].append("%s 对话的格式不对，导致无法提取" % _rt_talk_data[1])
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
        result = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            queryset.filter(status=1).update(extract_tag=1)
            queryset = queryset.filter(status=0)
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

                    else:
                        result['false'] += 1
                        result['error'].append("%s 对话的格式不对，导致无法提取" % _rt_talk_data[1])
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
    list_filter = ['shop', 'customer', 'start_time', 'end_time', 'min', 'dialog_tag__name']
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
                                dialog_detial.status = 1
                            else:
                                dialog_detial.status = 0
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
                            if dialog_order.end_time == end_time:
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
                                dialog_detial.status = 1
                            else:
                                dialog_detial.status = 0
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
    list_display = ['dialog_tb', 'sayer', 'status', 'time', 'interval', 'content', 'index', 'sensitive_tag', 'order_status']
    list_filter = ['dialog_tb__customer', 'index', 'extract_tag', 'sensitive_tag', 'sayer', 'status', 'time',
                   'interval', 'content']
    search_fields = ['dialog_tb__customer']
    actions = [CheckAction]

    def queryset(self):
        queryset = super(CheckODTBAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, sensitive_tag=0)
        return queryset


# 淘宝异常对话界面
class ExceptionODTBAdmin(object):
        list_display = ['dialog_tb', 'sayer', 'status', 'time', 'interval', 'content', 'index', 'sensitive_tag',
                        'order_status']
        list_filter = ['dialog_tb__customer', 'index', 'extract_tag', 'sensitive_tag', 'sayer', 'status', 'time',
                       'interval', 'content']
        search_fields = ['dialog_tb__customer']

        def queryset(self):
            queryset = super(ExceptionODTBAdmin, self).queryset()
            queryset = queryset.filter(is_delete=0, sensitive_tag=1, index__gt=0)
            return queryset


# 淘宝对话明细订单提取界面
class ExtractODTBAdmin(object):
    list_display = ['dialog_tb', 'mistake_tag', 'sayer', 'status', 'time', 'interval', 'content', 'index',
                    'sensitive_tag', 'order_status']
    list_filter = ['dialog_tb__customer', 'index', 'extract_tag', 'sensitive_tag', 'sayer', 'status', 'time',
                   'interval', 'content']
    search_fields = ['dialog_tb__customer']
    readonly_fields = ['dialog_tb', 'mistake_tag', 'sayer', 'status', 'time', 'interval', 'index', 'sensitive_tag',
                       'order_status', 'creator', 'extract_tag']
    list_editable = ['content']
    actions = [ExtractODTBAction, PassODJDAction]

    def queryset(self):
        queryset = super(ExtractODTBAdmin, self).queryset()
        queryset = queryset.filter(extract_tag=0)
        return queryset


# 淘宝对话明细订单提取界面
class MyExtractODTBAdmin(object):
    list_display = ['dialog_tb', 'mistake_tag', 'sayer', 'status', 'time', 'interval', 'content', 'index',
                    'sensitive_tag', 'order_status']
    list_filter = ['dialog_tb__customer', 'index', 'extract_tag', 'sensitive_tag', 'sayer', 'status', 'time',
                   'interval', 'content']
    search_fields = ['dialog_tb__customer']
    readonly_fields = ['dialog_tb', 'mistake_tag', 'sayer', 'status', 'time', 'interval', 'index', 'sensitive_tag',
                       'order_status', 'creator', 'extract_tag']
    list_editable = ['content']
    actions = [ExtractODTBAction, PassODJDAction]

    def queryset(self):
        queryset = super(MyExtractODTBAdmin, self).queryset()
        queryset = queryset.filter(extract_tag=0, creator=self.request.user.username)
        return queryset


# 淘宝对话明细查询界面
class OriDetailTBAdmin(object):
    list_display = ['dialog_tb', 'sayer', 'status', 'time', 'interval', 'content', 'index', 'extract_tag',
                    'sensitive_tag', 'order_status']
    list_filter = ['dialog_tb__customer', 'mistake_tag', 'category', 'create_time', 'index', 'extract_tag', 'sensitive_tag', 'sayer', 'status',
                   'time', 'interval', 'content']
    search_fields = ['dialog_tb__customer']
    readonly_fields = ['dialog_tb', 'sayer', 'status', 'time', 'interval', 'content', 'index', 'extract_tag',
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
    list_display = ['shop', 'customer', 'start_time', 'end_time', 'min', 'dialog_tag']
    list_filter = ['shop', 'customer', 'start_time', 'end_time', 'min', 'dialog_tag__name']
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
                                customer = str(dialog_contents[rank][0])
                                _q_customer = ServicerInfo.objects.filter(name=customer)
                                if _q_customer.exists():
                                    rank += 1
                                    continue
                                else:
                                    dialog_content.append(content)
                                    dialog_contents.append(dialog_content)
                                    dialog_content = []
                                    content = ''
                                    break
                        except Exception as e:
                            report_dic['error'].append('机器人无回应留言丢弃。 %s' % e)
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
                        if dialog_content[0] == customer:
                            dialog_detial.status = 1
                        else:
                            dialog_detial.status = 0
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
                        if i < 7:
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
    list_display = ['dialog_jd', 'sayer', 'status', 'time', 'interval', 'content', 'index', 'sensitive_tag', 'order_status']
    list_filter = ['dialog_jd__customer', 'index', 'extract_tag', 'sensitive_tag', 'sayer', 'status', 'time',
                   'interval', 'content']
    search_fields = ['dialog_jd__customer']
    actions = [CheckAction]

    def queryset(self):
        queryset = super(CheckODJDAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, sensitive_tag=0)
        return queryset


# 异常对话界面
class ExceptionODJDAdmin(object):
    list_display = ['dialog_jd', 'sayer', 'status', 'time', 'interval', 'content', 'index', 'sensitive_tag',
                    'order_status']
    list_filter = ['dialog_jd__customer', 'index', 'extract_tag', 'sensitive_tag', 'sayer', 'status', 'time',
                   'interval', 'content']
    search_fields = ['dialog_jd__customer']

    def queryset(self):
        queryset = super(ExceptionODJDAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, sensitive_tag=1, index__gt=0)
        return queryset


# 订单提取界面
class ExtractODJDAdmin(object):
    list_display = ['dialog_jd', 'mistake_tag', 'sayer', 'status', 'time', 'interval', 'content', 'index', 'sensitive_tag', 'order_status']
    list_filter = ['dialog_jd__customer', 'index', 'extract_tag', 'sensitive_tag', 'sayer', 'status', 'time',
                   'interval', 'content']
    search_fields = ['dialog_jd__customer']
    readonly_fields = ['dialog_jd', 'mistake_tag', 'sayer', 'status', 'time', 'interval', 'index', 'sensitive_tag', 'order_status', 'creator', 'extract_tag']
    list_editable = ['content']
    actions = [ExtractODJDAction, PassODJDAction]

    def queryset(self):
        queryset = super(ExtractODJDAdmin, self).queryset()
        queryset = queryset.filter(extract_tag=0)
        return queryset


# 京东对话明细
class OriDetailJDAdmin(object):
    list_display = ['dialog_jd', 'sayer', 'status', 'time', 'interval', 'content', 'index', 'extract_tag', 'sensitive_tag', 'order_status']
    list_filter = ['dialog_jd__customer', 'mistake_tag', 'category', 'index', 'extract_tag', 'sensitive_tag', 'sayer', 'status', 'time', 'interval', 'content']
    search_fields = ['dialog_jd__customer']
    readonly_fields = ['dialog_jd', 'sayer', 'category', 'create_time', 'status', 'time', 'interval', 'content', 'index', 'extract_tag', 'sensitive_tag', 'order_status', 'creator', 'is_delete', 'mistake_tag']
    actions = [ResetODJDExtract, ResetODJDSensitive]


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

