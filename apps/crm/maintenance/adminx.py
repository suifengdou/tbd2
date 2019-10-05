# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 20:58
# @Author  : Hann
# @Site    : 
# @File    : xadmin.py.py
# @Software: PyCharm

import math, re
import datetime
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count, Sum
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

from .models import MaintenanceInfo, MaintenanceHandlingInfo, MaintenanceSummary, MaintenanceSubmitInfo, \
    MaintenanceCalcInfo, MaintenanceJudgeInfo


class SubmitAction(BaseActionView):
    QUERY_FIELD = ['machine_sn', 'maintenance_order_id', 'warehouse', 'completer', 'maintenance_type', 'fault_type',
                   'appraisal', 'shop', 'ori_create_time', 'finish_time', 'buyer_nick', 'sender_name', 'sender_mobile',
                   'sender_area', 'goods_name', 'is_guarantee']
    action_name = "submit_selected"
    description = '递交选中的原始单'

    delete_confirmation_template = None
    delete_selected_confirmation_template = None

    modify_models_batch = True

    model_perm = 'change'
    icon = 'fa fa-flag'

    @filter_hook
    def do_action(self, queryset):
        report_dic_towork = {"successful": 0, "ori_successful": 0, "false": 0, "ori_order_error": 0, "repeat_num": 0,
                             "error": []}

        creator = self.request.user.username
        # Check that the user has change permission for the actual model
        if not self.has_change_permission():
            raise PermissionDenied

        n = queryset.count()
        if n:
            for order in queryset:
                # 创建一个工作台订单对象，
                handling_order = MaintenanceHandlingInfo()
                if MaintenanceHandlingInfo.objects.filter(maintenance_order_id=order.maintenance_order_id).exists():
                    report_dic_towork["repeat_num"] += 1
                    try:
                        ori_orders = MaintenanceInfo.objects.all().filter(
                            maintenance_order_id=order.maintenance_order_id, towork_status=0)
                        for ori_order in ori_orders:
                            ori_order.towork_status = 1
                            ori_order.save()
                            report_dic_towork["ori_successful"] += 1
                    except Exception as e:
                        report_dic_towork["error"].append(e)
                        report_dic_towork["ori_order_error"] += 1
                    continue
                # 对原单字段进行直接赋值操作。排除machine_sn，此字段单独进行处理。包含了空值。
                for key in self.__class__.QUERY_FIELD[1:]:
                    if hasattr(handling_order, key):
                        re_val = order.__getattribute__(key)
                        if re_val is None:
                            report_dic_towork["error"] = "递交订单出现了不可预料的内部错误！"
                        else:
                            setattr(handling_order, key, re_val)
                # 处理省市区
                _pre_area = str(order.sender_area).split(" ")
                if len(_pre_area) == 3:
                    handling_order.province = _pre_area[0]
                    handling_order.city = _pre_area[1]
                    handling_order.district = _pre_area[2]
                elif len(_pre_area) == 2:
                    handling_order.province = _pre_area[0]
                    handling_order.city = _pre_area[1]
                else:
                    pass
                # 处理产品名称
                _pre_goods_name = re.findall(r'([A-Z][\w\s-]+)', order.goods_name)
                if _pre_goods_name:
                    handling_order.goods_type = _pre_goods_name[0]
                else:
                    handling_order.goods_type = "未知"

                # 处理货品sn码，
                if re.match(r'^[0-9a-zA-Z]{8,}', str(order.machine_sn).strip(" ")):
                    handling_order.machine_sn = str(order.machine_sn).upper().strip(" ")
                else:
                    handling_order.machine_sn = ""

                handling_order.creator = creator
                # 处理日期的年月日
                _pre_time = order.finish_time
                handling_order.finish_date = _pre_time.strftime("%Y-%m-%d")
                handling_order.finish_month = _pre_time.strftime("%Y-%m")
                handling_order.finish_year = _pre_time.strftime("%Y")

                try:
                    handling_order.save()
                    report_dic_towork["successful"] += 1
                    try:
                        ori_orders = MaintenanceInfo.objects.all().filter(
                            maintenance_order_id=order.maintenance_order_id, towork_status=0)
                        for ori_order in ori_orders:
                            ori_order.towork_status = 1
                            ori_order.save()
                            report_dic_towork["ori_successful"] += 1
                    except Exception as e:
                        report_dic_towork["error"].append(e)
                        report_dic_towork["ori_order_error"] += 1
                except Exception as e:
                    report_dic_towork["error"].append(e)
                    report_dic_towork["false"] += 1
                self.log('change', '', order)

            self.message_user("成功递交 %(count)d %(items)s." % {
                "count": report_dic_towork['successful'], "items": model_ngettext(self.opts, n)
            }, 'success')
            self.message_user('成功更新了 %s 条原始单数据' % report_dic_towork['ori_successful'], 'success')
            if report_dic_towork['false'] > 0:
                self.message_user('失败了 %s 条数据' % report_dic_towork['false'], 'error')
            if report_dic_towork['ori_order_error'] > 0:
                self.message_user('更新失败了 %s 条原始单数据' % report_dic_towork['ori_order_error'], 'error')
            if report_dic_towork['repeat_num'] > 0:
                self.message_user('重复丢弃了 %s 条数据' % report_dic_towork['repeat_num'], 'error')
            if report_dic_towork['error']:
                self.message_user('主要错误是 %s ' % report_dic_towork['error'], 'error')

        # Return None to display the change list page again.
        return None


class CalcAction(BaseActionView):
    QUERY_FIELD = ['machine_sn', 'maintenance_order_id', 'warehouse', 'completer', 'maintenance_type', 'fault_type',
                   'appraisal', 'shop', 'ori_create_time', 'finish_time', 'buyer_nick', 'sender_name', 'sender_mobile',
                   'sender_area', 'goods_name', 'is_guarantee']
    action_name = "sign_selected"
    description = '标记选中的原始单'

    delete_confirmation_template = None
    delete_selected_confirmation_template = None

    model_perm = 'change'
    icon = 'fa fa-flag'

    @filter_hook
    def do_action(self, queryset):
        report_dic_totag = {"successful": 0, "tag_successful": 0, "false": 0, "torepeatsave": 0, "error": []}

        creator = self.request.user.username
        # Check that the user has change permission for the actual model
        if not self.has_change_permission():
            raise PermissionDenied

        # 按照未处理的标记，查询出表单对未处理订单。对订单的时间进行处理。
        days_range = queryset.values("finish_date").annotate(machine_num=Count("finish_date")).values(
            "finish_date", "machine_num").order_by("finish_date")
        if days_range:
            days = []
            for day in days_range:
                days.append(day["finish_date"])

            min_date = min(days)
            max_date = max(days) + datetime.timedelta(days=1)
            current_date = min_date
            verify_date = min_date - datetime.timedelta(days=1)

            verify_summary = MaintenanceSummary.objects.all().filter(finish_time=verify_date)
            if MaintenanceSummary.objects.first() is not None:
                if not verify_summary.exists():
                    return self.message_user('亲，请按照时间顺序进行递交计算，别胡搞行吗。', 'error')

            while current_date < max_date:
                repeat_dic = {"successful": 0, "tag_successful": 0, "false": 0, "error": []}

                # 当前天减去一天，作为前一天，作为前三十天的基准时间。
                end_date = current_date - datetime.timedelta(days=1)
                start_date = current_date.date() - datetime.timedelta(days=31)
                # 查询近三十天到所有单据，准备进行匹配查询。
                maintenance_checked = MaintenanceHandlingInfo.objects.filter(finish_time__gte=start_date,
                                                                         finish_time__lte=end_date)

                # 创建二次维修率的表单对象，
                verify_condition = MaintenanceSummary.objects.all().filter(finish_time=current_date)
                current_update_orders = queryset.filter(finish_date=current_date)
                if verify_condition.exists():
                    current_summary = verify_condition[0]
                    current_summary.order_count += current_update_orders.count()
                    try:
                        current_summary.save()
                        repeat_dic['error'].append("%s 更新了这个日期的当日保修单数量，之前保修单导入时有遗漏！" % (current_date))
                    except Exception as e:
                        repeat_dic['error'].append(e)
                else:
                    current_summary = MaintenanceSummary()
                    current_summary.finish_time = current_date
                    current_summary.order_count = current_update_orders.count()
                    current_summary.creator = creator
                    try:
                        current_summary.save()
                    except Exception as e:
                        repeat_dic['error'].append(e)

                # 首先生成统计表，然后更新累加统计表在每个循环。然后查询出二次维修，则检索二次维修当天统计表，进而更新二次维修数量。
                # 当天的二次维修检查数量，是发现二次维修数量，而不是当天的二次维修数量，是客户在当天的不满意数量。
                # 循环当前天的订单数据，根据当前天的sn查询出前三十天的二次维修问题。
                current_summary = MaintenanceSummary.objects.all().filter(finish_time=current_date)[0]
                for order in current_update_orders:
                    if len(order.machine_sn) < 5:
                        try:
                            order.handling_status = 1
                            order.save()
                            repeat_dic['successful'] += 1
                            continue
                        except Exception as e:
                            repeat_dic['error'].append(e)
                            repeat_dic['false'] += 1
                            continue
                    result_checked = maintenance_checked.filter(machine_sn=order.machine_sn, repeat_tag=0)
                    if result_checked.exists():
                        number = result_checked.count()
                        current_summary.repeat_found += number
                        for repeat_order in result_checked:
                            current_repeat_summary = MaintenanceSummary.objects.all().filter(finish_time=repeat_order.finish_date)[0]
                            current_repeat_summary.repeat_today += 1
                            current_repeat_summary.creator = creator
                            repeat_order.repeat_tag = 1
                            try:
                                repeat_order.save()
                                current_repeat_summary.save()
                                current_summary.save()
                            except Exception as e:
                                repeat_dic['error'].append(e)

                        try:
                            order.handling_status = 1
                            order.save()
                            repeat_dic['successful'] += 1
                            result_checked.update(repeat_tag=1)
                            repeat_dic['tag_successful'] += number
                        except Exception as e:
                            repeat_dic['error'].append(e)
                            repeat_dic['false'] += number
                    else:
                        try:
                            order.handling_status = 1
                            order.save()
                            repeat_dic['successful'] += 1
                        except Exception as e:
                            repeat_dic['error'].append(e)
                            repeat_dic['false'] += 1

                # 对数据进行汇总，累加到repeat_dic_total的字典里面
                report_dic_totag['successful'] += repeat_dic['successful']
                report_dic_totag['false'] +=repeat_dic['false']
                report_dic_totag['tag_successful'] = repeat_dic['tag_successful']
                report_dic_totag['torepeatsave'] += 1
                if repeat_dic['error']:
                    report_dic_totag['error'].append(repeat_dic['error'])

                current_date = current_date + datetime.timedelta(days=1)

            self.message_user('成功了递交 %s 条单据' % report_dic_totag['successful'], 'success')
            self.message_user('成功更新了 %s 条单据' % report_dic_totag['tag_successful'], 'success')
            self.message_user('计算了 %s 天统计数据' % report_dic_totag['torepeatsave'], 'success')
            if report_dic_totag['false'] > 0:
                self.message_user('失败了 %s 条单据' % report_dic_totag['false'], 'error')
            if report_dic_totag['error']:
                self.message_user('主要错误是 %s ' % report_dic_totag['error'], 'error')

        # Return None to display the change list page again.
        return None


class MaintenanceInfoAdmin(object):
    list_display = ['maintenance_order_id', 'warehouse', 'completer', 'maintenance_type', 'fault_type', 'machine_sn',
                    'appraisal', 'shop', 'finish_time', 'buyer_nick', 'sender_mobile', 'goods_name', 'is_guarantee']
    search_fields = ['maintenance_order_id', 'sender_mobile']
    list_filter = ['warehouse', 'fault_type', 'appraisal', 'finish_time']


class MaintenanceSubmitInfoAdmin(object):
    INIT_FIELDS_DIC = {
        "保修单号": "maintenance_order_id",
        "保修单状态": "order_status",
        "收发仓库": "warehouse",
        "处理登记人": "completer",
        "保修类型": "maintenance_type",
        "故障类型": "fault_type",
        "送修类型": "transport_type",
        "序列号": "machine_sn",
        "换新序列号": "new_machine_sn",
        "发货订单编号": "send_order_id",
        "保修结束语": "appraisal",
        "关联店铺": "shop",
        "购买时间": "purchase_time",
        "创建时间": "ori_create_time",
        "创建人": "ori_creator",
        "审核时间": "handle_time",
        "审核人": "handler_name",
        "保修完成时间": "finish_time",
        "保修金额": "fee",
        "保修数量": "quantity",
        "最后修改时间": "last_handle_time",
        "客户网名": "buyer_nick",
        "寄件客户姓名": "sender_name",
        "寄件客户手机": "sender_mobile",
        "寄件客户省市县": "sender_area",
        "寄件客户地址": "sender_address",
        "收件物流公司": "send_logistics_company",
        "收件物流单号": "send_logistics_no",
        "收件备注": "send_memory",
        "寄回客户姓名": "return_name",
        "寄回客户手机": "return_mobile",
        "寄回省市区": "return_area",
        "寄回地址": "return_address",
        "寄件指定物流公司": "return_logistics_company",
        "寄件物流单号": "return_logistics_no",
        "寄件备注": "return_memory",
        "保修货品商家编码": "goods_id",
        "保修货品名称": "goods_name",
        "保修货品简称": "goods_abbreviation",
        "故障描述": "description",
        "是否在保修期内": "is_guarantee",
        "收费状态": "charge_status",
        "收费金额": "charge_amount",
        "收费说明": "charge_memory"
    }
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    list_display = ['maintenance_order_id', 'towork_status', 'warehouse', 'completer', 'maintenance_type', 'fault_type',
                    'machine_sn', 'appraisal', 'shop']

    search_fields = ['maintenance_order_id', 'sender_mobile']
    list_filter = ['warehouse', 'fault_type', 'appraisal', 'finish_time']
    import_data = True
    actions = [SubmitAction, ]

    def post(self, request, *args, **kwargs):
        creator = request.user.username
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(file, creator)
            self.message_user('导入成功数据%s条' % result['successful'], 'success')
            if result['false'] > 0:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (result['false'], result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('包含更新重复数据%s条' % result['repeated'], 'error')
        return super(MaintenanceSubmitInfoAdmin, self).post(request, args, kwargs)

    def handle_upload_file(self, _file, creator):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            with pd.ExcelFile(_file) as xls:
                df = pd.read_excel(xls, sheet_name=0)

                # 获取表头，对表头进行转换成数据库字段名
                columns_key = df.columns.values.tolist()
                for i in range(len(columns_key)):
                    columns_key[i] = columns_key[i].replace(' ', '').replace('=', '')

                for i in range(len(columns_key)):
                    if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

                # 验证一下必要的核心字段是否存在
                _ret_verify_field = MaintenanceInfo.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field

                # 更改一下DataFrame的表名称
                columns_key_ori = df.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                df.rename(columns=ret_columns_key, inplace=True)

                num_end = 0
                num_step = 300
                num_total = len(df)

                for i in range(1, int(num_total / num_step) + 2):
                    num_start = num_end
                    num_end = num_step * i
                    intermediate_df = df.iloc[num_start: num_end]

                    # 获取导入表格的字典，每一行一个字典。这个字典最后显示是个list
                    _ret_list = intermediate_df.to_dict(orient='records')
                    intermediate_report_dic = self.save_resources(_ret_list, creator)
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
                    if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])
                # 直接调用验证函数进行验证
                _ret_verify_field = MaintenanceInfo.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field
                # 验证通过进行重新处理。
                columns_key_ori = piece.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                piece.rename(columns=ret_columns_key, inplace=True)
                _ret_list = piece.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(_ret_list, creator)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
            return report_dic

        else:
            return "只支持excel和csv文件格式！"

    def save_resources(self, resource, creator):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        # 开始导入数据
        for row in resource:
            # ERP导出文档添加了等于号，毙掉等于号。
            order = MaintenanceInfo()  # 创建表格每一行为一个对象
            for k, v in row.items():
                if re.match(r'^=', str(v)):
                    row[k] = v.replace('=', '').replace('"', '')

            maintenance_order_id = str(row["maintenance_order_id"])
            order_status = str(row["order_status"])
            purchase_time = str(row['purchase_time'])
            sender_mobile = str(row['sender_mobile'])
            return_mobile = str(row['return_mobile'])
            handle_time = str(row['handle_time'])

            # 状态不是'已完成', '待打印', '已打印'，就丢弃这个订单，计数为丢弃订单
            if order_status not in ['已完成', '待打印', '已打印']:
                report_dic["discard"] += 1
                continue
            # 如果存在保修完成时间，默认就是已完成。
            elif order_status in ['已完成', '待打印', '已打印']:
                row["order_status"] = '已完成'
            # 如果订单号查询，已经存在，丢弃订单，计数为重复订单
            if MaintenanceInfo.objects.filter(maintenance_order_id=maintenance_order_id).exists():
                report_dic["repeated"] += 1
                continue

            if len(str(row['description'])) > 500:
                row['description'] = row['description'][0:499]

            if purchase_time == '0000-00-00 00:00:00':
                row['purchase_time'] = '0001-01-01 00:00:00'

            if handle_time == '0000-00-00 00:00:00':
                row['handle_time'] = '0001-01-01 00:00:00'

            if "." in sender_mobile:
                row["sender_mobile"] = sender_mobile.split(".")[0]

            if "." in return_mobile:
                row['return_mobile'] = return_mobile.split(".")[0]

            for k, v in row.items():

                # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
                if hasattr(order, k):
                    if str(v) in ['nan', 'NaT']:
                        pass
                    else:
                        setattr(order, k, v)  # 更新对象属性为字典对应键值
            try:
                order.creator = creator
                order.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["error"].append(e)
                report_dic["false"] += 1
        return report_dic

    def queryset(self):
        queryset = super(MaintenanceSubmitInfoAdmin, self).queryset()
        queryset = queryset.filter(towork_status=0)
        return queryset


class MaintenanceCalcInfoAdmin(object):
    list_display = ['maintenance_order_id', 'finish_date', 'completer', 'maintenance_type', 'fault_type', 'machine_sn',
                    'appraisal', 'shop']

    search_fields = ['maintenance_order_id', 'sender_mobile']
    list_filter = ['warehouse', 'fault_type', 'appraisal', 'finish_time']
    ordering = ['finish_date']

    actions = [CalcAction, ]

    def queryset(self):
        queryset = super(MaintenanceCalcInfoAdmin, self).queryset()
        queryset = queryset.filter(handling_status=0)
        return queryset


class MaintenanceJudgeInfoAdmin(object):
    list_display = ['finish_date', 'repeat_tag', 'maintenance_order_id', 'machine_sn', 'appraisal',
                    'fault_type', 'completer', 'maintenance_type', 'shop']

    search_fields = ['maintenance_order_id', 'sender_mobile']
    list_filter = ['warehouse', 'fault_type', 'appraisal', 'finish_time']
    list_myeditable = ['repeat_tag']
    ordering = ['machine_sn', 'finish_date']

    def queryset(self):
        queryset = super(MaintenanceJudgeInfoAdmin, self).queryset()
        orders_repeat = queryset.filter(repeat_tag=1).values("machine_sn")
        sns_repeat = []
        for sn in orders_repeat:
            sns_repeat.append(sn['machine_sn'])
        queryset = queryset.filter(machine_sn__in=sns_repeat).all().order_by("machine_sn", "finish_time")
        return queryset


class MaintenanceHandlingInfoAdmin(object):
    list_display = ['maintenance_order_id', 'warehouse', 'maintenance_type', 'fault_type', 'machine_sn', 'appraisal',
                    'shop', 'finish_time', 'buyer_nick', 'sender_name', 'sender_mobile', 'sender_area', 'goods_name',
                    'is_guarantee', 'province', 'city', 'district', 'handling_status', 'repeat_tag', 'goods_type']
    search_fields = ['maintenance_order_id', 'sender_mobile']
    list_filter = ['shop', 'goods_type', 'finish_time', 'repeat_tag', 'handling_status']


class MaintenanceSummaryAdmin(object):
    list_display = ['finish_time', 'order_count', 'repeat_found', 'repeat_today']
    list_filter = ['finish_time']


xadmin.site.register(MaintenanceSubmitInfo, MaintenanceSubmitInfoAdmin)
xadmin.site.register(MaintenanceCalcInfo, MaintenanceCalcInfoAdmin)
xadmin.site.register(MaintenanceJudgeInfo, MaintenanceJudgeInfoAdmin)

xadmin.site.register(MaintenanceHandlingInfo, MaintenanceHandlingInfoAdmin)
xadmin.site.register(MaintenanceSummary, MaintenanceSummaryAdmin)
xadmin.site.register(MaintenanceInfo, MaintenanceInfoAdmin)
