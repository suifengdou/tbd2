# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    :
# @Software: PyCharm
# Create your views here.

import datetime
import csv
import re
import codecs
import json

from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http import HttpResponse, StreamingHttpResponse
# from .forms import UploadFileForm
from django.db.models import Q
from django.utils.six import moves



from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd


from .models import SFConsignation
from .forms import UploadFileForm


class ConsignationList(View):
    QUERY_FIELD = ["application_time", "consignor", "information", "remark",\
                   "feedback_time", "express_id", "is_operate", "handlingstatus", "create_time", "id", "creator"]

    def get(self, request: object) -> object:
        order_tag = request.GET.get("order_tag", '1')
        search_keywords = request.GET.get("search_keywords", None)
        num = request.GET.get("num", 10)
        num = int(num)
        download_tag = request.GET.get("download_tag", None)

        if num > 50:
            num = 50

        if search_keywords:
            all_service_orders = SFConsignation.objects.filter(express_id=search_keywords)

        elif order_tag == '0':
            all_service_orders = SFConsignation.objects.filter(handlingstatus=str(0)).values(*self.__class__.QUERY_FIELD).all().order_by('express_id')
        else:
            all_service_orders = SFConsignation.objects.values(*self.__class__.QUERY_FIELD).all().order_by('express_id')

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
            writer.writerow(['日期', '委托人', '信息', '异常知会', '反馈日期', '单号', '操作状态', '系统导入时间', '创建人'])
            for service_order in all_service_orders:
                writer.writerow([service_order['application_time'], service_order['consignor'], service_order['information'], \
                                 service_order['remark'], service_order['feedback_time'], service_order['express_id'], \
                                 service_order['handlingstatus'], service_order['create_time'], service_order['creator']])
            return response

        return render(request, "external/sf_consignation/consignationlist.html", {
            "all_service_orders": service_order,
            "index_tag": "ext_sf_consignation",
            "num": str(num),
            "order_tag": str(order_tag)
        })

    def post(self, request):
        pass


class OperateOrder(View):
    '''
    对订单 进行审核 直接进行ajax通信。
    '''
    def post(self, request):
        id = request.POST.get('id')
        try:
            service_order = SFConsignation.objects.get(id=int(id))
        except SFConsignation.DoesNotExist:
            return HttpResponse('{"status": "fail"}', content_type='application/json')
        service_order.handlingstatus = 1
        service_order.save()
        return HttpResponse('{"status": "success"}', content_type='application/json')


class ConsignationOverView(View):
    def get(self, request: object) -> object:
        finished_count = SFConsignation.objects.filter(handlingstatus=1).count()
        pending_count = SFConsignation.objects.filter(handlingstatus=0).count()

        return render(request, "external/sf_consignation/consignation-overview.html", {
            "index_tag": "ext_sf_consignation",
            "finished_count": finished_count,
            "pending_count": pending_count,

        })


class ConsignationUpLoad(View):
    INIT_FIELDS_DIC = {'日期': 'application_time', '委托人': 'consignor', '信息': 'information', '异常知会': 'remark',\
                       '是否操作': 'is_operate', '反馈日期': 'feedback_time', '单号': 'express_id',}
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    def get(self, request: object) -> object:
        return render(request, "external/sf_consignation/consignationupload.html", {
            "index_tag": "ext_sf_consignation",
        })

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            _result = self.handle_upload_file(request.FILES['file'])
            # 如果返回的是错误信息，就是字符串格式，直接执行下面的路径
            if isinstance(_result, str):
                return render(request, "external/sf_consignation/consignationupload.html", {
                    "messages": _result,
                    "index_tag": "ext_sf_consignation",
                })
            # 判断是数据列表的话，就执行保存操作。
            elif isinstance(_result, list):
                _result = self.save_resources(_result)
                return render(request, "external/sf_consignation/consignationupload.html", {
                    "report_dic": _result,
                    "index_tag": "ext_sf_consignation",
                })

        else:
            form = UploadFileForm()
        return render(request, "external/sf_consignation/consignationupload.html", {
            "messages": form,
            "index_tag": "ext_sf_consignation",
        })

    def handle_upload_file(self, _file):
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file)
            if len(df) > 60001:
                return "表格条数最大6000条，太多我就处理不来了。……__……!如果想要一次性导入大量数据，请联系管理员。"

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = SFConsignation.verify_mandatory(columns_key)
            if _ret_verify_field is not None:
                return _ret_verify_field

            # 更改一下DataFrame的表名称
            columns_key_ori = df.columns.values.tolist()
            ret_columns_key = dict(zip(columns_key_ori, columns_key))
            df.rename(columns=ret_columns_key, inplace=True)

            # 获取导入表格的字典，每一行一个字典。这个字典最后显示是个list
            _ret_list = df.to_dict(orient='records')
            return _ret_list
        else:
            pass

    @staticmethod
    def save_resources(resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0}

        # 开始导入数据
        for row in resource:
            service_order = SFConsignation()  # 创建表格每一行为一个对象
            express_id = str(row["express_id"])

            # 如果快递单号不符合规则，则丢弃
            if re.match(r'^[0-9]', express_id) is None:
                report_dic["discard"] += 1
                continue

            # 如果服务单号已经存在，丢弃订单，计数为重复订单
            elif SFConsignation.objects.filter(express_id=express_id).exists():
                report_dic["repeated"] += 1
                continue

            else:
                for k, v in row.items():

                    # 查询是否有这个字段属性，如果有就更新到对象。
                    if hasattr(service_order, k):
                        if str(v) in ['nan', 'NaT']:
                            pass
                        else:
                            setattr(service_order, k, v)  # 更新对象属性为字典对应键值
                try:
                    service_order.handling_status = 0  # 设置默认的操作状态。
                    service_order.save()
                    report_dic["successful"] += 1
                # 保存出错，直接错误条数计数加一。
                except Exception as e:
                    report_dic["false"] += 1

        return report_dic


