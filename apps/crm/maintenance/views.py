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

from apps.crm.maintenance.models import MaintenanceInfo, MaintenanceHandlingInfo, MaintenanceSummary
from .forms import UploadFileForm
# Create your views here.

class MaintenanceList(View):
    QUERY_FIELD = ["maintenance_order_id", "order_status", "shop", "purchase_time",
                   "finish_time", "buyer_nick", "sender_mobile", "goods_id", "goods_name",
                   "description", "is_guarantee", "tocustomer_status", "towork_status"]

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
                all_service_orders = MaintenanceInfo.objects.values(*self.__class__.QUERY_FIELD).all().order_by('maintenance_order_id')

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

    def get(self, request):
        elements = {"total_num": 0, "pending_num": 0, "repeat_num": 0, "unresolved_num": 0}
        total_num = MaintenanceInfo.objects.all().count()
        pending_num = MaintenanceInfo.objects.filter(towork_status=0).count()

        repeat_num = MaintenanceHandlingInfo.objects.all().count()
        unresolved_num = MaintenanceHandlingInfo.objects.filter(handling_status=0).count()

        print(elements)

        elements["total_num"] = total_num
        elements["pending_num"] = pending_num
        elements["repeat_num"] = repeat_num
        elements["unresolved_num"] = unresolved_num
        print(elements)

        return render(request, "crm/maintenance/upload.html", {
            "index_tag": "crm_maintenance_orders",
            "elements": elements,
        })

    def post(self, request):
        elements = {"total_num": 0, "pending_num": 0, "repeat_num": 0, "unresolved_num": 0}
        total_num = MaintenanceInfo.objects.all().count()
        pending_num = MaintenanceInfo.objects.filter(towork_status=0).count()

        repeat_num = MaintenanceHandlingInfo.objects.all().count()
        unresolved_num = MaintenanceHandlingInfo.objects.filter(handling_status=0).count()

        elements["total_num"] = total_num
        elements["pending_num"] = pending_num
        elements["repeat_num"] = repeat_num
        elements["unresolved_num"] = unresolved_num

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            _result = self.handle_upload_file(request.FILES['file'])
            # 如果返回的是错误信息，就是字符串格式，直接执行下面的路径
            if isinstance(_result, str):
                return render(request, "crm/maintenance/upload.html", {
                    "messages": _result,
                    "index_tag": "crm_maintenance_orders",
                    "element": elements,
                })
            # 判断是字典的话，就直接返回字典结果到前端页面。
            elif isinstance(_result, dict):
                return render(request, "crm/maintenance/upload.html", {
                    "report_dic": _result,
                    "index_tag": "crm_maintenance_orders",
                    "element": elements,
                })

        else:
            form = UploadFileForm()
        return render(request, "crm/maintenance/upload.html", {
            "messages": form,
            "index_tag": "crm_maintenance_orders",
            "element": elements,
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
            sender_mobile = str(row['sender_mobile'])
            return_mobile = str(row['return_mobile'])

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

            elif "." in sender_mobile:
                row["sender_mobile"] = sender_mobile.split(".")[0]

            elif "." in return_mobile:
                row['return_mobile'] = return_mobile.split(".")[0]

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
            "index_tag": "crm_maintenance_orders",
        })

    def post(self, request):
        pass


class MaintenanceHandlinglist(View):
    QUERY_FIELD = ["maintenance_order_id", "shop", "appraisal", "finish_time", "buyer_nick", "sender_mobile",
                   "goods_type", "goods_name", "is_guarantee", "handling_status", "repeat_tag", "machine_sn", "creator",
                   "create_time"]

    def get(self, request):
        order_tag = request.GET.get("order_tag", "1")
        search_keywords = request.GET.get("search_keywords", None)
        num = request.GET.get("num", 10)
        num = int(num)
        download_tag = request.GET.get("download_tag", None)

        if num > 50:
            num = 50

        if search_keywords:
            all_orders = MaintenanceHandlingInfo.objects.filter(
                Q(maintenance_order_id=search_keywords) | Q(sender_mobile=search_keywords)
            )
        else:
            if order_tag == "0":
                all_orders = MaintenanceHandlingInfo.objects.filter(handling_status=str(0)).values(
                    *self.__class__.QUERY_FIELD).all().order_by("-")
            else:
                all_orders = MaintenanceHandlingInfo.objects.values(*self.__class__.QUERY_FIELD).all().order_by('maintenance_order_id')

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orders, num, request=request)
        order = p.page(page)

        if download_tag:

            # 导出文件取名
            now = datetime.datetime.now()
            now = str(now)
            name = now.replace(':', '')

            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="{}.csv"'.format(name)

            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)
            writer.writerow(['保修单号', '店铺', '结束语', '完成时间', '网名', '寄件人电话', '货品型号', '货品名称',
                             '是否在保', '重复维修标记', '机器SN'])
            for order in all_orders:
                writer.writerow([order['maintenance_order_id'], order['shop'], order['appraisal'], order['finish_time'],
                                 order['buyer_nick'], order['sender_mobile'], order['goods_type'], order['goods_name'],
                                 order['is_guarantee'], order['repeat_tag'], order['machine_sn']])
            return response

        return render(request, "crm/maintenance/handlinglist.html", {
            "all_orders": order,
            "index_tag": "crm_maintenance_orders",
            "num": str(num),
            "order_tag": str(order_tag)
        })


class MaintenanceToWork(View):
    QUERY_FIELD = ['maintenance_order_id', 'warehouse', 'maintenance_type', 'fault_type', 'machine_sn', 'appraisal',
                   'shop', 'ori_create_time', 'finish_time', 'buyer_nick', 'sender_name', 'sender_mobile',
                   'sender_area', 'goods_name', 'is_guarantee']

    def post(self, request):
        # 定义递交工作台订单的报告字典，以及整体的数据的报告字典
        report_dic_towork = {"successful": 0, "ori_successful": 0, "false": 0, "ori_order_error": 0, "repeat_num": 0, "error": []}
        command_id = request.POST.get("towork", None)
        elements = {"total_num": 0, "pending_num": 0, "repeat_num": 0, "unresolved_num": 0}

        if command_id == '1':
            pending_orders = MaintenanceInfo.objects.values(*self.__class__.QUERY_FIELD).filter(towork_status="0")
            for order in pending_orders:
                # 创建一个工作台订单对象，
                handling_order = MaintenanceHandlingInfo()

                repetition = MaintenanceHandlingInfo.objects.filter(maintenance_order_id=order["maintenance_order_id"])
                if repetition:
                    report_dic_towork["repeat_num"] += 1
                    try:
                        ori_order = MaintenanceInfo.objects.get(maintenance_order_id=order["maintenance_order_id"])
                        ori_order.towork_status = 1
                        ori_order.save()
                        report_dic_towork["ori_successful"] += 1
                    except Exception as e:
                        report_dic_towork["error"].append(e)
                        report_dic_towork["ori_order_error"] += 1
                    continue
                # 对原单字段进行直接赋值操作。
                for key in self.__class__.QUERY_FIELD:
                    if hasattr(handling_order, key):
                        re_val = order.get(key, None)
                        if re_val is None:
                            report_dic_towork["error"] = "递交订单出现了不可预料的内部错误！"
                        else:
                            setattr(handling_order, key, re_val)
                # 处理省市区
                _pre_area = order["sender_area"].split(" ")
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
                _pre_goods_name = re.findall(r'([A-Z][\w\s-]+)', order["goods_name"])
                if _pre_goods_name:
                    handling_order.goods_type = _pre_goods_name[0]
                else:
                    handling_order.goods_type = "未知"

                # 处理货品sn码，
                if re.match(r'^[\w]+$',order["machine_sn"].strip(" ")):
                    handling_order.machine_sn = order["machine_sn"].upper().strip(" ")
                else:
                    handling_order.machine_sn = ""

                # 处理日期的年月日
                _pre_time = order["finish_time"]
                handling_order.finish_date = _pre_time.strftime("%Y-%m-%d")
                handling_order.finish_month = _pre_time.strftime("%Y-%m")
                handling_order.finish_year = _pre_time.strftime("%Y")

                try:
                    handling_order.save()
                    report_dic_towork["successful"] += 1
                    try:
                        ori_order = MaintenanceInfo.objects.get(maintenance_order_id=order["maintenance_order_id"])
                        ori_order.towork_status = 1
                        ori_order.save()
                        report_dic_towork["ori_successful"] += 1
                    except Exception as e:
                        report_dic_towork["error"].append(e)
                        report_dic_towork["ori_order_error"] += 1
                except Exception as e:
                    report_dic_towork["error"].append(e)
                    report_dic_towork["false"] += 1

            # 整体数据的报告字典，对维修单进行基础性统计，罗列在网页上。所有订单数，未递交数，二次维修数，未核定二次维修原因数等
            total_num = MaintenanceInfo.objects.all().count()
            pending_num = MaintenanceInfo.objects.filter(towork_status=0).count()

            repeat_num = MaintenanceHandlingInfo.objects.all().count()
            unresolved_num = MaintenanceHandlingInfo.objects.filter(handling_status=0).count()

            elements["total_num"] = total_num
            elements["pending_num"] = pending_num
            elements["repeat_num"] = repeat_num
            elements["unresolved_num"] = unresolved_num

            print(report_dic_towork)

            return render(request, "crm/maintenance/upload.html", {
                "index_tag": "crm_maintenance_orders",
                "elements": elements,
                "report_dic_towork": report_dic_towork,
            })

        else:

            total_num = MaintenanceInfo.objects.all().count()
            pending_num = MaintenanceInfo.objects.filter(towork_status=0).count()

            repeat_num = MaintenanceHandlingInfo.objects.all().count()
            unresolved_num = MaintenanceHandlingInfo.objects.filter(handling_status=0).count()

            elements["total_num"] = total_num
            elements["pending_num"] = pending_num
            elements["repeat_num"] = repeat_num
            elements["unresolved_num"] = unresolved_num
            report_dic_towork['error'] = '请联系管理员，出现了内部错误'

            render(request, '', {
                "report_dic_towork": report_dic_towork,
                "elements": elements,
            })



class MaintenanceSignRepeat(View):
    def post(self, request):
        report_dic_totag = {"successful": 0, "tag_successful": 0, "false": 0, "torepeatsave": 0, "error": []}
        command_id = request.POST.get("signrepeat", None)
        elements = {"total_num": 0, "pending_num": 0, "repeat_num": 0, "unresolved_num": 0}







        #
        # today = datetime.datetime.now().date()
        # weekdelta = datetime.datetime.now().date() - datetime.timedelta(weeks=3)
        # maintenance_quantity = MaintenanceInfo.objects.filter(finish_time__gte=weekdelta, finish_time__lte=today)
        # print(maintenance_quantity)
        #
        # test = MaintenanceInfo.objects.filter(finish_time__gte=weekdelta, finish_time__lte=today).aggregate(
        #     "machine_sn").values("machine_sn")
        # print(test)
        #
        if command_id == '1':
            # 按照未处理的标记，查询出表单对未处理订单。对订单的时间进行处理。
            days_range = MaintenanceHandlingInfo.objects.values("finish_date").filter(handling_status=0).annotate(machine_num=Count("finish_date")).values("finish_date", "machine_num").order_by("finish_date")
            days = []
            for day in days_range:
                days.append(day["finish_date"])

            min_date = min(days)
            max_date = max(days) + datetime.timedelta(days=1)
            current_date = min_date

            while current_date < max_date:
                # 当前天减去一天，作为前一天，作为前三十天到基准时间。
                current_date = min_date - datetime.timedelta(days=1)
                _pre_thirtyday = current_date.date() - datetime.timedelta(days=31)
                # 查询近三十天到所有sn码，准备进行匹配查询。
                maintenance_msn = MaintenanceHandlingInfo.objects.values("machine_sn", "finish_date").filter(finish_time__gte=_pre_thirtyday, finish_time__lte=current_date)

                total_num = maintenance_msn.count()
                # 创建sn码列表，汇总所有近三十天的sn码加入到列表中，
                machine_sns = []
                for machine_sn in maintenance_msn:
                    _pre_msn = maintenance_msn["machine_sn"].upper().strip()

                    if re.match(r'^[\w]', _pre_msn):
                        machine_sns.append(maintenance_msn["machine_sn"])
                # 恢复为当前天，查询当前天到sn码，准备进行查询。
                current_date = min_date + datetime.timedelta(days=1)
                current_orders = MaintenanceHandlingInfo.objects.all().filter(finish_time=current_date)
                # 查询当前天的订单对象集。准备进行循环处理。
                for current_order in current_orders:
                    if current_order.machine_sn in machine_sns:
                        current_order.repeat_tag = 1
                        current_order.handling_status = 1
                        report_dic_totag["tag_successful"] += 1

                    else:
                        current_order.handling_status = 1

                    current_order.save()
                    report_dic_totag["successful"] += 1

                # 创建二次维修率的表单对象，对当前天的数据进行保存，未来不再重复计算。
                current_summary = MaintenanceSummary()
                current_summary.finish_date = current_date
                current_summary.thirty_day_count = total_num
                current_summary.repeat_count = report_dic_totag["tag_successful"]

                current_summary.save()
                report_dic_totag["torepeatsave"] += 1


                current_date = min_date + datetime.timedelta(days=1)




            # days = []
            # for day in days_range:
            #     print(day["finish_date"])
            #     days.append(day["finish_date"].strftime("%Y-%m-%d"))
            # print(days)
            # print(min(days))

            # a = min(days)
            # a_day = datetime.datetime.strptime(a, "%Y-%m-%d")
            # # print(a_day)
            # delta = datetime.timedelta(days=1)
            # b = a_day + delta
            # print(b)
            # print(b.strftime("%Y-%m-%d"))
            # print(max(days))





            delta = datetime.timedelta(days=1)

            print(delta)





            pass

        #
        #
        #         try:
        #             handling_order.save()
        #             report_dic_towork["successful"] += 1
        #             try:
        #                 ori_order = MaintenanceInfo.objects.get(maintenance_order_id=order["maintenance_order_id"])
        #                 ori_order.towork_status = 1
        #                 ori_order.save()
        #                 report_dic_towork["ori_successful"] += 1
        #             except Exception as e:
        #                 report_dic_towork["error"].append(e)
        #                 report_dic_towork["ori_order_error"] += 1
        #         except Exception as e:
        #             report_dic_towork["error"].append(e)
        #             report_dic_towork["false"] += 1
        #
        #     整体数据的报告字典，对维修单进行基础性统计，罗列在网页上。所有订单数，未递交数，二次维修数，未核定二次维修原因数等
        #     total_num = MaintenanceInfo.objects.all().count()
        #     pending_num = MaintenanceInfo.objects.filter(towork_status=0).count()
        #
        #     repeat_num = MaintenanceHandlingInfo.objects.all().count()
        #     unresolved_num = MaintenanceHandlingInfo.objects.filter(handling_status=0).count()
        #
        #     elements["total_num"] = total_num
        #     elements["pending_num"] = pending_num
        #     elements["repeat_num"] = repeat_num
        #     elements["unresolved_num"] = unresolved_num
        #
        #     print(report_dic_towork)

        #     return render(request, "crm/maintenance/upload.html", {
        #         "index_tag": "crm_maintenance_orders",
        #         "elements": elements,
        #         "report_dic_towork": report_dic_towork,
        #     })
        #
        # else:
        #
        #     total_num = MaintenanceInfo.objects.all().count()
        #     pending_num = MaintenanceInfo.objects.filter(towork_status=0).count()
        #
        #     repeat_num = MaintenanceHandlingInfo.objects.all().count()
        #     unresolved_num = MaintenanceHandlingInfo.objects.filter(handling_status=0).count()
        #
        #     elements["total_num"] = total_num
        #     elements["pending_num"] = pending_num
        #     elements["repeat_num"] = repeat_num
        #     elements["unresolved_num"] = unresolved_num
        #     report_dic_towork['error'] = '请联系管理员，出现了内部错误'
        #
        #     render(request, '', {
        #         "report_dic_towork": report_dic_towork,
        #         "elements": elements,
        #     })




class MaintenanceWorkList(View):
    pass