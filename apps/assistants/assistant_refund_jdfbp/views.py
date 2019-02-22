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

from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http import HttpResponse, StreamingHttpResponse
from .forms import UploadFileForm
from django.db.models import Q
from django.utils.six import moves



from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd


from .models import RefundResource


class RefundList(View):
    QUERY_FIELD = ["service_order_id", "order_id", "goods_name", "order_status",
                   "express_id", "express_company", "handlingstatus", "create_time", "id"]

    def get(self, request):
        order_tag = request.GET.get("order_tag", '1')
        search_keywords = request.GET.get("search_keywords", None)
        num = request.GET.get("num", 10)
        num = int(num)
        download_tag = request.GET.get("download_tag", None)

        if num > 50:
            num = 50

        if search_keywords:
            all_service_orders = RefundResource.objects.filter(
                Q(service_order_id=search_keywords) | Q(order_id=search_keywords) | Q(express_id=search_keywords)
            )
        else:

            if order_tag == '0':
                all_service_orders = RefundResource.objects.filter(handlingstatus=str(0)).values(*self.__class__.QUERY_FIELD).all().order_by('order_id')
            else:
                all_service_orders = RefundResource.objects.values(*self.__class__.QUERY_FIELD).all().order_by('order_id')

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
            writer.writerow(['服务单号', '订单编号', '货品名称', '服务单状态', '快递单号', '快递公司', '操作状态', '系统导入时间', ''])
            for service_order in all_service_orders:
                writer.writerow([service_order['service_order_id'], service_order['order_id'], service_order['goods_name'], \
                                 service_order['order_status'], service_order['express_id'], service_order['express_company'], \
                                 service_order['handlingstatus'], service_order['create_time']])
            return response

        return render(request, "assis/refund_jdfbp/refundlist.html", {
            "all_service_orders": service_order,
            "index_tag": "ass_jdfbp_service",
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
            service_order = RefundResource.objects.get(id=int(id))
        except RefundResource.DoesNotExist:
            return HttpResponse('{"status": "fail"}', content_type='application/json')
        service_order.handlingstatus = 1
        service_order.save()
        return HttpResponse('{"status": "success"}', content_type='application/json')


class RefundOverView(View):
    def get(self, request):
        finished_count = RefundResource.objects.filter(handlingstatus=1).count()
        pending_count = RefundResource.objects.filter(handlingstatus=0).count()

        return render(request, "assis/refund_jdfbp/refund-overview.html", {
            "index_tag": "ass_jdfbp_service",
            "finished_count": finished_count,
            "pending_count": pending_count,

        })


class RefundUpLoad(View):
    INIT_FIELDS_DIC = {'服务单号': 'service_order_id', '订单号': 'order_id', '商品编号': 'goods_id', '商品名称': 'goods_name',
                       '商品金额': 'goods_amount', '服务单状态': 'order_status', '售后服务单申请时间': 'application_time',
                       '商家首次审核时间': 'bs_initial_time', '商家首次处理时间': 'bs_handle_time', '售后服务单整体时长': 'duration',
                       '审核结果': 'bs_result', '处理结果描述': 'bs_result_desc', '客户预期处理方式': 'buyer_expectation',
                       '返回方式': 'return_model', '客户问题描述': 'buyer_problem_desc', '最新审核时间': 'last_handle_time',
                       '审核意见': 'handle_opinion', '审核人姓名': 'handler_name', '取件时间': 'take_delivery_time',
                       '取件状态': 'take_delivery_status', '发货时间': 'delivery_time', '运单号': 'express_id',
                       '运费金额': 'express_fee', '快递公司': 'express_company', '商家收货时间': 'receive_time',
                       '收货登记原因': 'refund_reason', '收货人': 'receiver', '处理人': 'completer',
                       '退款金额': 'refund_amount', '换新订单': 'renew_express_id', '换新商品编号': 'renew_goods_id',
                       '是否闪退订单': 'is_quick_refund'}
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']


    def get(self, request):

        return render(request, "assis/refund_jdfbp/refundupload.html", {
            "index_tag": "ass_jdfbp_service",
        })

    def post(self, request):

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            _result = self.handle_upload_file(request.FILES['file'])
            # 如果返回的是错误信息，就是字符串格式，直接执行下面的路径
            if isinstance(_result, str):
                return render(request, "assis/refund_jdfbp/refundupload.html", {
                    "messages": _result,
                    "index_tag": "ass_jdfbp_service",
                })
            # 判断是数据列表的话，就执行保存操作。
            elif isinstance(_result, list):
                _result = self.save_resources(_result)
                return render(request, "assis/refund_jdfbp/refundupload.html", {
                    "report_dic": _result,
                    "index_tag": "ass_jdfbp_service",
                })

        else:
            form = UploadFileForm()
        return render(request, "assis/refund_jdfbp/refundupload.html", {
            "messages": form,
            "index_tag": "ass_jdfbp_service",
        })

    def handle_upload_file(self, _file):
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file)
            if len(df) > 10001:
                return "表格条数最大10000条，太多我就处理不来了。……__……!如果想要一次性导入大量数据，请联系管理员。"

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = RefundResource.verify_mandatory(columns_key)
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
            service_order = RefundResource()  # 创建表格每一行为一个对象
            express_id = str(row["express_id"])
            service_order_id = str(row["service_order_id"])

            # 如果服务单号为空，就丢弃这个订单，计数为丢弃订单
            if re.match(r'^[0-9VW]', service_order_id) is None:
                report_dic["discard"] += 1
                continue

            # 如果服务单号已经存在，丢弃订单，计数为重复订单
            elif RefundResource.objects.filter(service_order_id=service_order_id).exists():
                report_dic["repeated"] += 1
                continue

            # 如果快递单号为空，则丢弃
            elif re.match(r'^[0-9VW]', express_id) is None:
                report_dic["discard"] += 1
                continue

            else:
                for k, v in row.items():

                    # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
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





