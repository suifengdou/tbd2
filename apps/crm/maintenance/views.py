# -*- coding: utf-8 -*-
# @Time    : 2019/02/22 16:52
# @Author  : Hann
# @Site    :
# @Software: PyCharm
# Create your views here.
import csv, datetime, codecs, re


from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Q, Sum, Count, Avg
from django.utils.six import moves
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd

from apps.crm.maintenance.models import MaintenanceInfo
from .forms import UploadFileForm
# Create your views here.

class MaintenanceList(View):
    QUERY_FIELD = ["maintenance_order_id", "order_status", "shop", "purchase_time",
                   "finish_time", "buyer_nick", "sender_mobile", "goods_id", "goods_name",
                   "description", "is_guarantee", "tocustomer_status", "toproduct_status"]

    def get(self, request):
        order_tag = request.GET.get("order_tag", '1')
        search_keywords = request.GET.get("search_keywords", None)
        num = request.GET.get("num", 10)
        num = int(num)
        download_tag = request.GET.get("download_tag", None)

        if num > 50:
            num = 50

        if search_keywords:
            all_service_orders = MaintenanceInfo.objects.filter(
                Q(maintenance_order_id=search_keywords) | Q(send_logistics_no=search_keywords) | Q\
                    (sender_mobile=search_keywords)
            )
        else:

            if order_tag == '0':
                all_service_orders = MaintenanceInfo.objects.filter(handlingstatus=str(0)).values\
                    (*self.__class__.QUERY_FIELD).all().order_by('maintenance_order_id')
            else:
                all_service_orders = MaintenanceInfo.objects.values(*self.__class__.QUERY_FIELD).all().order_by\
                    ('maintenance_order_id')

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_service_orders, num, request=request)
        service_order = p.page(page)

        if download_tag:

            # 导出文件取名
            now = datetime.datetime.now()
            now = str(now)
            name = now.replace(':', '')

            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="{}.csv"'.format(name)

            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)
            writer.writerow(['保修单号', '保修单状态', '店铺', '购买时间', '完成时间', '网名', '寄件人电话', '货品ID',
                             '货品名称', '故障描述', '是否在保'])
            for service_order in all_service_orders:
                writer.writerow([service_order['maintenance_order_id'], service_order['order_status'],
                                 service_order['shop'], service_order['purchase_time'], service_order['finish_time'],
                                 service_order['buyer_nick'], service_order['sender_mobile'], service_order['goods_id'],
                                 service_order['goods_name'], service_order['description'],
                                 service_order['is_guarantee']])
            return response

        return render(request, "crm/maintenance/list.html", {
            "all_service_orders": service_order,
            "index_tag": "crm_maintenance_orders",
            "num": str(num),
            "order_tag": str(order_tag)
        })

    def post(self, request):
        pass


class MaintenanceUpload(View):
    INIT_FIELDS_DIC = {
        "保修单号": "maintenance_order_id",
        "保修单状态": "order_status",
        "收发仓库": "warehouse",
        "是否已处理过": "completer",
        "保修类型": "maintenance_type",
        "故障类型": "fault_type",
        "送修类型": "transport_type",
        "序列号": "machine_sn",
        "换新序列号": "new_machine_sn",
        "发货订单编号": "send_order_id",
        "保修结束语": "appraisal",
        "关联店铺": "shop",
        "购买时间": "purchase_time",
        "创建时间": "create_time",
        "创建人": "creator",
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

    def get(self, request):

        return render(request, "crm/maintenance/upload.html", {
            "index_tag": "crm_maintenance_orders",
        })

    def post(self, request):

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            _result = self.handle_upload_file(request.FILES['file'])
            # 如果返回的是错误信息，就是字符串格式，直接执行下面的路径
            if isinstance(_result, str):
                return render(request, "crm/maintenance/upload.html", {
                    "messages": _result,
                    "index_tag": "crm_maintenance_orders",
                })
            # 判断是字典的话，就直接返回字典结果到前端页面。
            elif isinstance(_result, dict):
                return render(request, "crm/maintenance/upload.html", {
                    "report_dic": _result,
                    "index_tag": "crm_maintenance_orders",
                })

        else:
            form = UploadFileForm()
        return render(request, "crm/maintenance/upload.html", {
            "messages": form,
            "index_tag": "crm_maintenance_orders",
        })

    def handle_upload_file(self, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            with pd.ExcelFile(_file) as xls:
                df = pd.read_excel(xls, sheet_name='Sheet1')

                # 获取表头，对表头进行转换成数据库字段名
                columns_key = df.columns.values.tolist()
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
            df = pd.read_csv(_file, encoding="ANSI", chunksize=300)

            for piece in df:
                columns_key = piece.columns.values.tolist()
                for i in range(len(columns_key)):
                    if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])
                _ret_verify_field = MaintenanceInfo.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field
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
            # ERP导出文档添加了等于号，毙掉等于号。
            order = MaintenanceInfo()  # 创建表格每一行为一个对象
            for k, v in row.items():
                if re.match(r'^=', str(v)):
                    row[k] = v.replace('=', '').replace('"', '')

            maintenance_order_id = str(row["maintenance_order_id"])
            order_status = str(row["order_status"])
            purchase_time = str(row['purchase_time'])

            # 状态不是已完成，就丢弃这个订单，计数为丢弃订单
            if order_status != '已完成':
                report_dic["discard"] += 1
                continue

            # 如果订单号查询，已经存在，丢弃订单，计数为重复订单
            elif MaintenanceInfo.objects.filter(maintenance_order_id=maintenance_order_id).exists():
                report_dic["repeated"] += 1
                continue

            elif len(str(row['description'])) > 500:
                row['description'] = row['description'][0:499]

            elif purchase_time == '0000-00-00 00:00:00':
                row['purchase_time'] = '0001-01-01 00:00:00'

            for k, v in row.items():

                # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
                if hasattr(order, k):
                    if str(v) in ['nan', 'NaT']:
                        pass
                    else:
                        setattr(order, k, v)  # 更新对象属性为字典对应键值
            try:
                order.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["error"].append(e)
                report_dic["false"] += 1
        return report_dic


class MaintenanceOverview(View):
    def get(self, request):
        m_total = {}
        today = datetime.datetime.now().date()
        weekdelta = datetime.datetime.now().date() - datetime.timedelta(weeks=3)
        maintenance_quantity = MaintenanceInfo.objects.filter(finish_time__gte=weekdelta, finish_time__lte=today)
        print(maintenance_quantity)

        test = MaintenanceInfo.objects.filter(finish_time__gte=weekdelta, finish_time__lte=today).values("finish_time").annotate(quantity=Count('maintenance_order_id')).values("finish_time", "quantity").order_by("finish_time")
        print(test)

        _rt_summary_quantity = {}
        for date_data in test:
            date_str = date_data["finish_time"].strftime("%Y-%m-%d")
            quantity = date_data["quantity"]
            if _rt_summary_quantity.get(date_str, None) is None:
                _rt_summary_quantity[date_str] = quantity
            else:
                _rt_summary_quantity[date_str] += quantity
        print(_rt_summary_quantity)
        rt_summary_quantity_d = []
        rt_summary_quantity_q = []
        for d, q in _rt_summary_quantity.items():
            rt_summary_quantity_d.append(d)
            rt_summary_quantity_q.append(q)
        print(rt_summary_quantity_d)
        print(rt_summary_quantity_q)

        m_total["rt_summary_quantity_d"] = rt_summary_quantity_d
        m_total["rt_summary_quantity_q"] = rt_summary_quantity_q



        return render(request, "crm/maintenance/overview.html", {
            "m_total": m_total,
        })

    def post(self, request):
        pass
