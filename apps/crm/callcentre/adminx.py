# -*- coding: utf-8 -*-
# @Time    : 2019/7/8 15:38
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import re
import datetime
from django.core.exceptions import PermissionDenied

import pandas as pd
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side
import emoji

from .models import OriCallLogInfo, CheckOriCall
from apps.assistants.giftintalk.models import OrderCallList, GiftInTalkInfo


# 明细提取订单
class ExtractAction(BaseActionView):
    action_name = "extract_ori_call"
    description = "提取选中的单据"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    modify_models_batch = False



    @filter_hook
    def do_action(self, queryset):
        result = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            categroy = {'质量问题': 1, '开箱即损': 2, '礼品赠品': 3}
            for obj in queryset:
                if obj.service_info:
                    if obj.result == '未选择队列':
                        result['discard'] += 1
                        obj.order_status = 2
                        obj.save()
                        continue
                    if not obj.shop:
                        result["false"] += 1
                        obj.mistake_tag = 3
                        obj.save()
                        continue
                    if obj.reason:
                        if OrderCallList.objects.filter(call_order=obj).exists():
                            result["false"] += 1
                            obj.mistake_tag = 1
                            obj.save()
                            continue
                        else:
                            order_list_call = OrderCallList()
                    else:
                        result['false'] += 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                else:
                    result['discard'] += 1
                    obj.order_status = 2
                    obj.save()
                    continue
                parts_order = GiftInTalkInfo()
                _check_data = re.findall(r'{(.*?)}', str(obj.service_info), re.DOTALL)

                if len(_check_data) == 4:
                    parts_order.goods = _check_data[0]
                    parts_order.cs_information = _check_data[1]
                    parts_order.broken_part = _check_data[2]
                    parts_order.description = _check_data[3]
                elif len(_check_data) == 2:
                    parts_order.goods = _check_data[0]
                    parts_order.cs_information = _check_data[1]
                else:
                    result['false'] += 1
                    obj.mistake_tag = 4
                    obj.save()
                    continue

                order_category = categroy.get(obj.reason, None)
                if order_category:
                    parts_order.order_category = order_category
                else:
                    result['false'] += 1
                    obj.mistake_tag = 5
                    obj.save()
                    continue

                parts_order.servicer = obj.customer_service
                parts_order.nickname = obj.mobile
                parts_order.platform = 4
                parts_order.shop = obj.shop
                parts_order.m_sn = obj.goods_id

                try:

                    parts_order.creator = self.request.user.username
                    parts_order.save()
                    order_list_call.gift_order = parts_order
                    order_list_call.call_order = obj
                    order_list_call.creator = self.request.user.username
                    order_list_call.save()
                    result["successful"] += 1
                    obj.content_category = 1
                except Exception as e:
                    result["false"] += 1
                    result["error"].append(e)
                    obj.mistake_tag = 6
                    obj.content_category = 1
                    obj.save()
                    continue
                obj.order_status = 2
                obj.save()
            self.message_user(result)
            self.message_user("提交 %(count)d %(items)s。" % {"count": n, "items": model_ngettext(self.opts, n)}, 'success')

        return None


class CheckOriCallAdmin(object):
    list_display = ['call_time', 'mistake_tag', 'mobile', 'service_info', 'reason', 'shop', 'location', 'relay_number',
                    'customer_service', 'call_category', 'source', 'line_up_status', 'line_up_time',
                    'device_status', 'result', 'recorder', 'call_length', 'message',
                    'relevant_cs', 'work_order', 'description', 'group']

    list_filter = ['creator', 'mistake_tag', 'service_info', 'create_time', 'order_status', 'customer_service',
                   'call_category', 'source', 'line_up_status', 'device_status', 'theme', 'degree_satisfaction',
                   'leading_cadre', 'group', 'call_id']
    search_fields = ['mobile']
    list_editable = ['service_info', 'reason', 'shop']
    actions = [ExtractAction]

    form_layout = [
        Fieldset('基本信息',
                 Row('mobile', 'call_time', 'call_category', 'result',),
                 Row('line_up_time', 'ring_time', 'call_length',),),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    INIT_FIELDS_DIC = {
        "时间": "call_time",
        "客户电话": "mobile",
        "归属地": "location",
        "中继号": "relay_number",
        "客服": "customer_service",
        "通话类型": "call_category",
        "来源": "source",
        "任务": "task",
        "排队状态": "line_up_status",
        "排队耗时": "line_up_time",
        "设备状态": "device_status",
        "通话结果": "result",
        "外呼失败原因": "failure_reason",
        "通话录音": "call_recording",
        "通话时长": "call_length",
        "留言": "message",
        "响铃时间": "ring_time",
        "通话挂断方": "ring_off",
        "满意度评价": "degree_satisfaction",
        "主题": "theme",
        "顺振": "sequence_ring",
        "相关客服": "relevant_cs",
        "生成工单": "work_order",
        "邮箱": "email",
        "标签": "tag",
        "描述": "description",
        "负责人": "leading_cadre",
        "负责组": "group",
        "等级": "degree",
        "是否在黑名单": "is_blacklist",
        "CallID": "call_id",
        "补寄原因": "reason",
        "来电类别": "call_class",
        "商品型号": "goods_name",
        "处理方式": "process_category",
        "产品编号": "goods_id",
        "购买日期": "purchase_time",
        "补寄配件记录": "service_info",
        "店铺": "shop",
    }
    import_data = True

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('导入结果 %s' % result, 'success')
        return super(CheckOriCallAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0)

            FILTER_FIELDS = ['时间', '客户电话', '归属地', '中继号', '客服', '通话类型', '来源', '排队状态', '排队耗时', '设备状态',
                             '通话结果', '外呼失败原因', '通话录音', '通话时长', '留言', '响铃时间', '通话挂断方', '满意度评价',
                             '主题', '顺振', '相关客服', '生成工单', '邮箱', '标签', '描述', '负责人', '负责组', '等级',
                             '是否在黑名单', 'call_id']

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
            _ret_verify_field = OriCallLogInfo.verify_mandatory(columns_key)
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
                    columns_key[i] = columns_key[i].replace(' ', '').replace('=', '').replace("*", "")
                # 循环处理对应的预先设置，转换成数据库字段名称
                for i in range(len(columns_key)):
                    if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])
                # 直接调用验证函数进行验证
                _ret_verify_field = OriCallLogInfo.verify_mandatory(columns_key)
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
            row['call_id'] = str(row["call_id"]).replace('\t', '')
            _q_call = OriCallLogInfo.objects.filter(call_id=row['call_id'])
            if _q_call.exists():
                report_dic['repeated'] += 1
                continue
            row['mobile'] = str(row['mobile']).replace(' ', '')
            row['relay_number'] = str(row['relay_number']).replace(' ', '')
            order = OriCallLogInfo()
            for k, v in row.items():
                # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
                if hasattr(order, k):
                    if str(v) in ['nan', 'NaT']:
                        pass
                    else:
                        setattr(order, k, v)  # 更新对象属性为字典对应键值
            try:
                order.creator = request.user.username
                order.save()
                report_dic['successful'] += 1
            except Exception as e:
                report_dic['error'].append(e)
                report_dic['false'] += 1
                continue

        return report_dic

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.servicer = request.user.username
        obj.order_status = 1
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(CheckOriCallAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset


class OriCallLogInfoAdmin(object):
    list_display = ['call_time', 'mobile', 'location', 'relay_number', 'customer_service', 'call_category', 'source',
                    'line_up_status', 'line_up_time', 'device_status', 'result', 'failure_reason', 'recorder',
                    'call_length', 'message', 'ring_time', 'ring_off', 'degree_satisfaction', 'theme', 'sequence_ring',
                    'relevant_cs', 'work_order', 'email', 'tag', 'description', 'leading_cadre', 'group', 'degree',
                    'is_blacklist']

    list_filter = ['creator', 'create_time', 'order_status', 'customer_service', 'call_category', 'source',
                   'line_up_status', 'device_status', 'theme', 'degree_satisfaction', 'leading_cadre', 'group',
                   'call_id', ]
    search_fields = ['mobile']

    form_layout = [
        Fieldset('基本信息',
                 Row('mobile', 'call_time', 'call_category', 'result',),
                 Row('line_up_time', 'ring_time', 'call_length',),),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]
    readonly_fields = ['call_time', 'mobile', 'location', 'relay_number', 'customer_service', 'call_category', 'source',
                       'line_up_status', 'line_up_time', 'device_status', 'result', 'failure_reason', 'call_recording',
                       'call_length', 'message', 'ring_time', 'ring_off', 'degree_satisfaction', 'theme', 'sequence_ring',
                       'relevant_cs', 'work_order', 'email', 'tag', 'description', 'leading_cadre', 'group', 'degree',
                       'is_blacklist', 'call_id', 'creator', 'create_time', 'update_time', 'is_delete',]


xadmin.site.register(CheckOriCall, CheckOriCallAdmin)
xadmin.site.register(OriCallLogInfo, OriCallLogInfoAdmin)