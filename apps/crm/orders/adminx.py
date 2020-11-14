# -*- coding: utf-8 -*-
# @Time    : 2020/10/10 17:37
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
from django.db.models import Sum, Avg, Min, Max, F

from django.contrib.admin.utils import get_deleted_objects

from django.core.files.uploadedfile import InMemoryUploadedFile

import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side


from .models import OriOrderInfo, SimpleOrderInfo, SubmitOriOrder


class SubmitOriOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']

    list_filter = ['buyer_nick', 'receiver_mobile', 'deliver_time', 'goods_name', 'spec_code', 'num', 'price',
                   'share_amount', 'src_tids', ]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {
        '客户网名': 'buyer_nick',
        '订单编号': 'trade_no',
        '收件人': 'receiver_name',
        '收货地址': 'receiver_address',
        '收件人手机': 'receiver_mobile',
        '发货时间': 'deliver_time',
        '付款时间': 'pay_time',
        '收货地区': 'receiver_area',
        '物流单号': 'logistics_no',
        '买家留言': 'buyer_message',
        '客服备注': 'cs_remark',
        '原始子订单号': 'src_tids',
        '货品数量': 'num',
        '货品成交价': 'price',
        '货品成交总价': 'share_amount',
        '货品名称': 'goods_name',
        '商家编码': 'spec_code',
        '店铺': 'shop_name',
        '物流公司': 'logistics_name',
        '仓库': 'warehouse_name',
        '订单类型': 'order_category',

    }

    import_data = True

    def post(self, request, *args, **kwargs):

        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('结果提示：%s' % result)
        return super(SubmitOriOrderAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ['客户网名', '订单编号', '收件人', '收货地址', '收件人手机', '发货时间', '付款时间', '收货地区',
                             '物流单号', '买家留言', '客服备注', '原始子订单号', '货品数量', '货品成交价', '货品成交总价', '货品名称',
                             '商家编码', '店铺', '物流公司', '仓库', '订单类型']

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
            _ret_verify_field = OriOrderInfo.verify_mandatory(columns_key)
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

        else:
            report_dic["error"].append('只支持excel文件格式！')
            return report_dic

    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}

        for row in resource:
            if row['trade_no'] == '合计:':
                continue
            if "0000-00-00" in str(row['pay_time']):
                row['pay_time'] = row['deliver_time']
            emo_fields = ['buyer_nick', 'receiver_name', 'receiver_address', 'buyer_message', 'cs_remark']
            for word in emo_fields:
                row[word] = emoji.demojize(str(row[word]))

            order_fields = ['buyer_nick', 'trade_no', 'receiver_name', 'receiver_address', 'receiver_mobile',
                            'deliver_time', 'pay_time', 'receiver_area', 'logistics_no', 'buyer_message', 'cs_remark',
                            'src_tids', 'num', 'price', 'share_amount', 'goods_name', 'spec_code', 'order_category',
                            'shop_name', 'logistics_name', 'warehouse_name']
            order = OriOrderInfo()
            for field in order_fields:
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
        queryset = super(SubmitOriOrderAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset


class OriOrderInfoAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']

    list_filter = ['buyer_nick', 'receiver_mobile', 'deliver_time', 'goods_name', 'spec_code', 'num', 'price',
                   'share_amount', 'src_tids',]

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


class SimpleOrderInfoAdmin(object):
    list_display = ['buyer_nick', 'cs_info', ]
    list_editable = []
    actions = []

    form_layout = [
        Fieldset('基本信息',
                 Row('buyer_nick',),
                 Row('cs_info',), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    batch_data = True
    nick_ids = []

    def post(self, request, *args, **kwargs):
        ids = request.POST.get('ids', None)
        if ids is not None:
            if " " in ids:
                ids = ids.split(" ")
                self.nick_ids = []
                self.nick_ids = ids
                self.queryset()
            else:
                self.nick_ids = []
                self.nick_ids.append(str(ids).replace("/t", "").replace("/n", "").replace(" ", ""))
                self.queryset()

        return super(SimpleOrderInfoAdmin, self).post(request, *args, **kwargs)

    def queryset(self):
        queryset = super(SimpleOrderInfoAdmin, self).queryset()

        if self.nick_ids:
            queryset = queryset.filter(is_delete=0, buyer_nick__in=self.nick_ids)
            if not queryset:
                queryset = super(SimpleOrderInfoAdmin, self).queryset().filter(is_delete=0, receiver_mobile__in=self.nick_ids)
        return queryset


xadmin.site.register(SubmitOriOrder, SubmitOriOrderAdmin)
xadmin.site.register(OriOrderInfo, OriOrderInfoAdmin)
xadmin.site.register(SimpleOrderInfo, SimpleOrderInfoAdmin)
