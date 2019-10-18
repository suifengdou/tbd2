# -*- coding: utf-8 -*-
# @Time    : 2019/02/22 16:52
# @Author  : Hann
# @Site    :
# @Software: PyCharm
# Create your views here.
import csv, datetime, codecs, re, time

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


from apps.utils.mixin_utils import LoginRequiredMixin


class MaintenanceList(LoginRequiredMixin, View):
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
                Q(maintenance_order_id=search_keywords) | Q(send_logistics_no=search_keywords) | Q \
                    (sender_mobile=search_keywords)
            )
        else:

            if order_tag == '0':
                all_service_orders = MaintenanceInfo.objects.filter(handlingstatus=str(0)).values \
                    (*self.__class__.QUERY_FIELD).all().order_by('maintenance_order_id')
            else:
                all_service_orders = MaintenanceInfo.objects.values(*self.__class__.QUERY_FIELD).all().order_by(
                    'maintenance_order_id')

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


class MaintenanceUpload(LoginRequiredMixin, View):
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

    def get(self, request):

        elements = MainUtils.elementsnum()

        return render(request, "crm/maintenance/upload.html", {
            "index_tag": "crm_maintenance_orders",
            "elements": elements,
        })

    def post(self, request):
        creator = request.user.username
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            _result = self.handle_upload_file(request.FILES['file'], creator)
            # 如果返回的是错误信息，就是字符串格式，直接执行下面的路径
            if isinstance(_result, str):

                elements = MainUtils.elementsnum()

                return render(request, "crm/maintenance/upload.html", {
                    "messages": _result,
                    "index_tag": "crm_maintenance_orders",
                    "elements": elements,
                })
            # 判断是字典的话，就直接返回字典结果到前端页面。
            elif isinstance(_result, dict):

                elements = MainUtils.elementsnum()

                return render(request, "crm/maintenance/upload.html", {
                    "report_dic": _result,
                    "index_tag": "crm_maintenance_orders",
                    "elements": elements,
                })

        else:
            form = UploadFileForm()

        elements = MainUtils.elementsnum()

        return render(request, "crm/maintenance/upload.html", {
            "messages": form,
            "index_tag": "crm_maintenance_orders",
            "elements": elements,
        })

    def handle_upload_file(self, _file, creator):
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


class MaintenanceOverview(LoginRequiredMixin, View):
    # 验证起始时间和截止时间
    def is_valid_datetime(self, start_time, end_time):
        try:
            if ":" in start_time:
                time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if ":" in end_time:
                time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            return True
        except:
            return False

    # 确认起始时间和截止时间
    def confirm_time(self, confirm_data):
        # 如果不是快捷选择，就是自定义选择。
        if confirm_data["week_num"] is None:
            # 对于自定义选择，获取起始时间和截止时间，进行格式验证和逻辑验证
            start_time = confirm_data["start_time"]
            end_time = confirm_data["end_time"]
            # 验证一下时间格式，如果成功。
            if self.is_valid_datetime(start_time, end_time):
                start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                d_value = end_time - start_time
                # 计算一下时间间隔，是否是三个月内。如果超出或者选择错误。
                if d_value.days in range(1, 91):
                    confirm_data["start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
                    confirm_data["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
                    confirm_data["tag_date"] = 0
                    return confirm_data
                else:
                    # 验证不符合规则，直接设置最近一周的快捷方式。
                    confirm_data["week_num"] = 1
                    confirm_data["error"] = "自定义的时间不能超过60天，或是负数，自动转换最近一周"

            else:
                # 验证不符合规则，直接设置最近一周的快捷方式。
                confirm_data["week_num"] = 1
                confirm_data["error"] = "自定义的时间格式错误，自动转换为最近一周"
        # 直接按照快捷选择的周数进行实践确认。
        confirm_data["tag_date"] = confirm_data["week_num"]
        confirm_data["end_time"] = datetime.datetime.now().date().strftime("%Y-%m-%d %H:%M:%S")
        confirm_data["start_time"] = (
            datetime.datetime.now().date() - datetime.timedelta(weeks=int(confirm_data["week_num"]))).strftime(
            "%Y-%m-%d %H:%M:%S")
        confirm_data["ori_start_time"] = confirm_data["start_time"].split(" ")[0]
        confirm_data["ori_end_time"] = confirm_data["end_time"].split(" ")[0]
        return confirm_data

    def get(self, request):

        m_total = {}
        confirm_data = {
            "week_num": request.GET.get("weeks_num", None),
            "start_time": request.GET.get("start_time", None),
            "end_time": request.GET.get("end_time", None)
        }
        if confirm_data["start_time"]:
            confirm_data["start_time"] = confirm_data["start_time"] + " 00:00:00"
        if confirm_data["end_time"]:
            confirm_data["end_time"] = confirm_data["end_time"] + " 00:00:00"
        confirm_data = self.confirm_time(confirm_data)
        m_total["confirm_data"] = confirm_data

        # 数据库进行查询块，决定数据范围和数据内容。
        # 首先查询handling表格的数据
        maintenance_quantity = MaintenanceHandlingInfo.objects.all().filter(
            finish_time__gte=datetime.datetime.strptime(confirm_data["start_time"], "%Y-%m-%d %H:%M:%S"),
            finish_time__lte=datetime.datetime.strptime(confirm_data["end_time"], "%Y-%m-%d %H:%M:%S"))
        # 然后查询二次维修量的表格
        repeat_quantity = MaintenanceSummary.objects.all().filter(
            finish_time__gte=datetime.datetime.strptime(confirm_data["start_time"], "%Y-%m-%d %H:%M:%S"),
            finish_time__lte=datetime.datetime.strptime(confirm_data["end_time"], "%Y-%m-%d %H:%M:%S"))
        # 计算maintenance的完成时间维度的数量
        rt_summary_date = []
        rt_summary_quantity = []
        rt_summary_repeat_found = []
        rt_summary_repeat_today = []
        rt_summary_ratio_repeat_f = []
        rt_summary_ratio_repeat_t = []
        for date_data in repeat_quantity:
            rt_summary_date.append(date_data.finish_time.strftime("%Y-%m-%d"))
            rt_summary_quantity.append(date_data.order_count)
            rt_summary_repeat_found.append(date_data.repeat_found)
            rt_summary_repeat_today.append(date_data.repeat_today)
            if date_data.order_count == 0:
                rt_summary_ratio_repeat_f.append(float('%.2f' % (0)))
                rt_summary_ratio_repeat_t.append(float('%.2f' % (0)))
            else:
                rt_summary_ratio_repeat_f.append(float('%.2f' % (date_data.repeat_found / date_data.order_count * 100)))
                rt_summary_ratio_repeat_t.append(float('%.2f' % (date_data.repeat_today / date_data.order_count * 100)))

        # 把维修数量做到汇总字典中
        m_total["rt_summary_date"] = rt_summary_date
        m_total["rt_summary_quantity"] = rt_summary_quantity
        m_total["rt_summary_repeat_found"] = rt_summary_repeat_found
        m_total["rt_summary_repeat_today"] = rt_summary_repeat_today
        m_total["rt_summary_ratio_repeat_f"] = rt_summary_ratio_repeat_f
        m_total["rt_summary_ratio_repeat_t"] = rt_summary_ratio_repeat_t

        # 维修型号下钻图
        total_num = maintenance_quantity.count()
        goods_type_num = maintenance_quantity.values("goods_type").annotate(
            quantity=Count("maintenance_order_id")).values("goods_type", "quantity").order_by("-quantity")

        # 型号数量占比数据
        goods_type_total = []
        # 下钻型号原因数据
        reason_goods_total = []
        # 型号数量数据
        goods_type_total_q = []
        # 下钻型号原因数量数据
        reason_goods_total_q = []

        for good_num in goods_type_num:
            goods_type_title = {"name": good_num["goods_type"],
                                "y": float('%.2f' % (good_num["quantity"] / total_num * 100)),
                                "drilldown": good_num["goods_type"]}

            if goods_type_title["y"] < 1:
                break
            goods_type_title_q = {"name": good_num["goods_type"],
                                  "y": int(good_num["quantity"]),
                                  "drilldown": good_num["goods_type"]
                                  }
            # 型号数量比例，和型号绝对数量循环录入到列表中
            goods_type_total.append(goods_type_title)
            goods_type_total_q.append(goods_type_title_q)
            # 具体型号的原因下钻数据，name,id,data(是一个列表），需要单独操作data
            reason_good = {"name": good_num["goods_type"], "id": good_num["goods_type"]}
            reason_good_q = {"name": good_num["goods_type"], "id": good_num["goods_type"]}
            # 特别创建data列表
            reason_good_data = []
            reason_good_data_q = []
            # 查出对应型号的对应保修单的对应故障原因的对应数量
            reason_nums = maintenance_quantity.filter(goods_type=good_num["goods_type"]).values("appraisal").annotate(
                quantity=Count("maintenance_order_id")).values("appraisal", "quantity").order_by("-quantity")

            reason_nums_total = good_num["quantity"]

            for reason in reason_nums:
                # 原因创建一个小列表
                reason_num = [reason["appraisal"], float("%.2f" % (reason["quantity"] / reason_nums_total * 100))]
                reason_num_q = [reason["appraisal"], int(reason["quantity"])]
                # 归属到原因的大列表中。
                reason_good_data.append(reason_num)
                reason_good_data_q.append(reason_num_q)
            reason_good["data"] = reason_good_data
            reason_good_q["data"] = reason_good_data_q
            reason_goods_total.append(reason_good)
            reason_goods_total_q.append(reason_good_q)

        # 把型号占比下钻图数据占比整合到total字典。
        m_total["goods_type_total"] = goods_type_total
        m_total["reason_goods_total"] = reason_goods_total
        # 把型号占比下钻图绝对数据整合到total字典。
        m_total["goods_type_total_q"] = goods_type_total_q
        m_total["reason_goods_total_q"] = reason_goods_total_q

        # 二次维修责任部门下钻图
        # 二次维修型号下钻图。
        responbility_departs = maintenance_quantity.filter(repeat_tag__in=[1, 2, 3, 4]).values("repeat_tag").annotate(
            quantity=Count("maintenance_order_id")).values("repeat_tag", "quantity")
        responbility_goods = maintenance_quantity.filter(repeat_tag__in=[1, 2, 3, 4]).values("goods_type").annotate(
            quantity=Count("maintenance_order_id")).values("goods_type", "quantity").order_by("-quantity")
        _pre_department = {
            "1": "未处理",
            "2": "产品",
            "3": "维修",
            "4": "客服"
        }
        responbility_depart_total = []
        responbility_goods_total = []
        repeat_goods_total = []
        repeat_goods_reason_total = []
        for respon_depart in responbility_departs:
            responbility_depart_title = {
                "name": _pre_department[str(respon_depart["repeat_tag"])],
                "y": int(respon_depart["quantity"]),
                "drilldown": _pre_department[str(respon_depart["repeat_tag"])]
            }
            responbility_depart_total.append(responbility_depart_title)

            respon_goods = {
                "name": _pre_department[str(respon_depart["repeat_tag"])],
                "id": _pre_department[str(respon_depart["repeat_tag"])],
            }
            respon_goods_data = []
            respon_goods_num = maintenance_quantity.filter(repeat_tag=respon_depart["repeat_tag"]).values(
                "goods_type").annotate(quantity=Count("maintenance_order_id")).values("goods_type",
                                                                                      "quantity").order_by("-quantity")
            for respon_good in respon_goods_num:
                respon_good_data = [respon_good["goods_type"], int(respon_good["quantity"])]
                respon_goods_data.append(respon_good_data)
            respon_goods["data"] = respon_goods_data
            repeat_goods_total.append(respon_goods)
        # 把二次维修的下钻图加入到大字典中
        m_total["responbility_depart_total"] = responbility_depart_total
        m_total["repeat_goods_total"] = repeat_goods_total

        for responbility_good in responbility_goods:
            responbility_good_title = {
                "name": responbility_good["goods_type"],
                "y": int(responbility_good["quantity"]),
                "drilldown": responbility_good["goods_type"]
            }
            responbility_goods_total.append(responbility_good_title)
            respon_reasons = {
                "name": responbility_good["goods_type"],
                "id": responbility_good["goods_type"],
            }
            respon_reasons_data = []
            respon_reasons_num = maintenance_quantity.exclude(repeat_tag=0).filter(
                goods_type=responbility_good["goods_type"]).values("appraisal").annotate(
                quantity=Count("maintenance_order_id")).values("appraisal", "quantity")
            for respon_reason in respon_reasons_num:
                respon_reason_data = [respon_reason["appraisal"], int(respon_reason["quantity"])]
                respon_reasons_data.append(respon_reason_data)
            respon_reasons["data"] = respon_reasons_data
            repeat_goods_reason_total.append(respon_reasons)
        # 把二次维修的下钻绝对数加入到大字典中，中央维修的图表就基本做完了
        m_total["responbility_goods_total"] = responbility_goods_total
        m_total["repeat_goods_reason_total"] = repeat_goods_reason_total

        # 二次维修的维修员数据
        repairer_repeat_total = []
        repairer_repeat_goods_total = []
        # 维修员完成数量共享了一个查询。
        repairer_repeat_num = maintenance_quantity.filter(repeat_tag__in=[1, 2, 3, 4]).values("completer").annotate(
            quantity=Count("maintenance_order_id")).values("completer", "quantity").order_by("-quantity")
        # 维修员完成数量的查询
        repairers_num = maintenance_quantity.values("completer").annotate(quantity=Count("maintenance_order_id")).values("completer", "quantity").order_by("-quantity")
        repairers_name = []
        repairer_repeat_name_num = []
        repairer_work_num = []
        repairer_repeat_dic = {}
        for repairer_repeat in repairer_repeat_num:
            repairer_repeat_title = {
                "name": repairer_repeat["completer"],
                "y": repairer_repeat["quantity"],
                "drilldown": repairer_repeat["completer"]
            }
            repairer_repeat_total.append(repairer_repeat_title)
            repairer_repeat_goods = {
                "name": repairer_repeat["completer"],
                "id": repairer_repeat["completer"],
            }
            repairer_repeat_goods_data = []
            repairer_goods_num = maintenance_quantity.exclude(repeat_tag=0).filter(
                completer=repairer_repeat["completer"]).values("goods_type").annotate(
                quantity=Count("maintenance_order_id")).values("goods_type", "quantity").order_by("-quantity")
            for repairer_goods_temp in repairer_goods_num:
                repairer_repeat_good_data = [repairer_goods_temp["goods_type"], int(repairer_goods_temp["quantity"])]
                repairer_repeat_goods_data.append(repairer_repeat_good_data)
            repairer_repeat_goods["data"] = repairer_repeat_goods_data
            repairer_repeat_goods_total.append(repairer_repeat_goods)

            # 维修员
            repairer_repeat_dic[repairer_repeat["completer"]] = repairer_repeat["quantity"]

        for repairer_num in repairers_num:
            repairers_name.append(repairer_num["completer"])
            repairer_work_num.append(repairer_num["quantity"])
        for repairer_name in repairers_name:
            repairer_repeat_name_num.append(repairer_repeat_dic.get(repairer_name, 0))

        m_total["repairer_repeat_total"] = repairer_repeat_total
        m_total["repairer_repeat_goods_total"] = repairer_repeat_goods_total

        m_total["repairers_name"] = repairers_name
        m_total["repairer_work_num"] = repairer_work_num
        m_total["repairer_repeat_name_num"] = repairer_repeat_name_num



        return render(request, "crm/maintenance/overview.html", {
            "m_total": m_total,
            "index_tag": "crm_maintenance_orders",
        })

    def post(self, request):
        pass


class MaintenanceHandlinglist(LoginRequiredMixin, View):
    QUERY_FIELD = ["maintenance_order_id", "completer", "shop", "appraisal", "finish_time", "buyer_nick",
                   "sender_mobile",
                   "goods_type", "goods_name", "is_guarantee", "handling_status", "repeat_tag", "machine_sn", "creator",
                   "create_time", "id"]

    def get(self, request: object) -> object:
        order_tag = request.GET.get("order_tag", "1")
        search_keywords = request.GET.get("search_keywords", None)
        num = request.GET.get("num", 10)
        num = int(num)
        download_tag = request.GET.get("download_tag", None)
        start_time = request.GET.get("start_time", None)
        end_time = request.GET.get("end_time", None)

        if num > 50:
            num = 50

        if search_keywords:
            all_orders = MaintenanceHandlingInfo.objects.filter(
                Q(maintenance_order_id=search_keywords) | Q(sender_mobile=search_keywords) | Q(
                    machine_sn=search_keywords)
            )
        elif start_time and end_time:
            # 如果查询的是二次维修订单，则同时增加一个时间一个维度查询
            if order_tag == "9":
                all_orders = MaintenanceHandlingInfo.objects.filter(finish_time__gte=start_time,
                                                                    finish_time__lte=end_time,
                                                                    repeat_tag__in=[1, 2, 3, 4]).order_by(
                    "-finish_time")
            # 如果不是查询二次维修订单，则直接一个时间维度查询。
            else:
                all_orders = MaintenanceHandlingInfo.objects.filter(finish_time__gte=start_time,
                                                                    finish_time__lte=end_time).order_by("-finish_time")

        else:
            # 如果订单标记为9，则取出所有标记为二次维修的订单。
            if order_tag == "9":
                all_orders = MaintenanceHandlingInfo.objects.filter(repeat_tag__in=[1, 2, 3, 4]).values(
                    *self.__class__.QUERY_FIELD).all().order_by("-finish_time")
            else:
                all_orders = MaintenanceHandlingInfo.objects.values(*self.__class__.QUERY_FIELD).all().order_by(
                    'maintenance_order_id')

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
            writer.writerow(['保修单号', '店铺', '结束语', '维修登记人', '完成时间', '网名', '寄件人电话', '货品型号', '货品名称',
                             '是否在保', '重复维修标记', '机器SN'])
            for order in all_orders:
                writer.writerow([order['maintenance_order_id'], order['shop'], order['completer'], order['appraisal'],
                                 order['finish_time'],
                                 order['buyer_nick'], order['sender_mobile'], order['goods_type'], order['goods_name'],
                                 order['is_guarantee'], order['repeat_tag'], order['machine_sn']])
            return response

        return render(request, "crm/maintenance/handlinglist.html", {
            "all_orders": order,
            "index_tag": "crm_maintenance_orders",
            "num": str(num),
            "order_tag": str(order_tag),
            "start_time": start_time,
            "end_time": end_time,
            "search_keywords": search_keywords,
        })


class MaintenanceToWork(LoginRequiredMixin, View):
    QUERY_FIELD = ['machine_sn', 'maintenance_order_id', 'warehouse', 'completer', 'maintenance_type', 'fault_type',
                   'appraisal', 'shop', 'ori_create_time', 'finish_time', 'buyer_nick', 'sender_name', 'sender_mobile',
                   'sender_area', 'goods_name', 'is_guarantee']

    def post(self, request):
        # 定义递交工作台订单的报告字典，以及整体的数据的报告字典
        report_dic_towork = {"successful": 0, "ori_successful": 0, "false": 0, "ori_order_error": 0, "repeat_num": 0,
                             "error": []}
        command_id = request.POST.get("towork", None)

        creator = request.user.username

        if command_id == '1':
            pending_orders = MaintenanceInfo.objects.values(*self.__class__.QUERY_FIELD).filter(towork_status=0)
            for order in pending_orders:
                # 创建一个工作台订单对象，
                handling_order = MaintenanceHandlingInfo()

                if MaintenanceHandlingInfo.objects.filter(maintenance_order_id=order["maintenance_order_id"]).exists():
                    report_dic_towork["repeat_num"] += 1
                    try:
                        ori_orders = MaintenanceInfo.objects.all().filter(
                            maintenance_order_id=order["maintenance_order_id"], towork_status=0)
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
                if re.match(r'^[0-9a-zA-Z]{8,}', str(order["machine_sn"]).strip(" ")):
                    handling_order.machine_sn = order["machine_sn"].upper().strip(" ")
                else:
                    handling_order.machine_sn = ""

                handling_order.creator = creator
                # 处理日期的年月日
                _pre_time = order["finish_time"]
                handling_order.finish_date = _pre_time.strftime("%Y-%m-%d")
                handling_order.finish_month = _pre_time.strftime("%Y-%m")
                handling_order.finish_year = _pre_time.strftime("%Y")

                try:
                    handling_order.save()
                    report_dic_towork["successful"] += 1
                    try:
                        ori_orders = MaintenanceInfo.objects.all().filter(
                            maintenance_order_id=order["maintenance_order_id"], towork_status=0)
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

            # 整体数据的报告字典，对维修单进行基础性统计，罗列在网页上。所有订单数，未递交数，二次维修数，未核定二次维修原因数等
            elements = MainUtils.elementsnum()

            return render(request, "crm/maintenance/upload.html", {
                "index_tag": "crm_maintenance_orders",
                "elements": elements,
                "report_dic_towork": report_dic_towork,
            })

        else:

            elements = MainUtils.elementsnum()

            return render(request, 'crm/maintenance/upload.html', {
                "index_tag": "crm_maintenance_orders",
                "report_dic_towork": report_dic_towork,
                "elements": elements,
            })


class MaintenanceSignRepeat(LoginRequiredMixin, View):
    def post(self, request):
        report_dic_totag = {"successful": 0, "tag_successful": 0, "false": 0, "torepeatsave": 0, "error": []}
        command_id = request.POST.get("signrepeat", None)

        if command_id == '1':
            # 按照未处理的标记，查询出表单对未处理订单。对订单的时间进行处理。
            days_range = MaintenanceHandlingInfo.objects.values("finish_date").filter(handling_status=0).annotate(
                machine_num=Count("finish_date")).values("finish_date", "machine_num").order_by("finish_date")
            if days_range:
                days = []
                for day in days_range:
                    days.append(day["finish_date"])

                min_date = min(days)
                max_date = max(days) + datetime.timedelta(days=1)
                current_date = min_date

                while current_date < max_date:
                    repeat_dic = {"repeat_num": 0}
                    # 当前天减去一天，作为前一天，作为前三十天到基准时间。
                    current_date = current_date - datetime.timedelta(days=1)
                    _pre_thirtyday = current_date.date() - datetime.timedelta(days=31)
                    # 查询近三十天到所有sn码，准备进行匹配查询。
                    maintenance_msn = MaintenanceHandlingInfo.objects.values("machine_sn", "finish_date").filter(
                        finish_time__gte=_pre_thirtyday, finish_time__lte=current_date)

                    total_num = maintenance_msn.count()
                    # 创建sn码列表，汇总所有近三十天的sn码加入到列表中，
                    machine_sns = []
                    for machine_sn in maintenance_msn:
                        _pre_msn = machine_sn["machine_sn"].upper().strip(" ")

                        if re.match(r'^[\w]', _pre_msn):
                            machine_sns.append(_pre_msn)
                    # 恢复为当前天，查询当前天到sn码，准备进行查询。
                    current_date = current_date + datetime.timedelta(days=1)
                    next_date = current_date + datetime.timedelta(days=1)
                    # 取出当前时间段的所有单据，需要锁定未进行标记过的订单，已经标记过的订单需要排除在外。
                    current_orders = MaintenanceHandlingInfo.objects.all().filter(finish_time__gte=current_date,
                                                                                  finish_time__lte=next_date,
                                                                                  repeat_tag=0)
                    # 查询当前天的订单对象集。准备进行循环处理。
                    for current_order in current_orders:
                        if current_order.machine_sn in machine_sns:
                            current_order.repeat_tag = 1
                            current_order.handling_status = 1
                            report_dic_totag["tag_successful"] += 1
                            repeat_dic["repeat_num"] += 1
                        else:
                            current_order.handling_status = 1

                        current_order.save()
                        report_dic_totag["successful"] += 1

                    # 创建二次维修率的表单对象，对当前天的数据进行保存，未来不再重复计算。
                    verify_condition = MaintenanceSummary.objects.all().filter(finish_time=current_date)

                    if verify_condition.exists():
                        report_dic_totag['error'].append("%s 已经计算过二次维修，重新递交了这个日期的保修单" % (current_date))
                    else:
                        current_summary = MaintenanceSummary()
                        current_summary.finish_time = current_date
                        current_summary.order_count = current_orders.count()
                        current_summary.thirty_day_count = total_num
                        current_summary.repeat_count = repeat_dic["repeat_num"]

                        current_summary.save()
                    report_dic_totag["torepeatsave"] += 1

                    current_date = current_date + datetime.timedelta(days=1)

                # 整体数据的报告字典，对维修单进行基础性统计，罗列在网页上。所有订单数，未递交数，二次维修数，未核定二次维修原因数等
                elements = MainUtils.elementsnum()

                return render(request, 'crm/maintenance/upload.html', {
                    "index_tag": "crm_maintenance_orders",
                    "report_dic_totag": report_dic_totag,
                    "elements": elements,
                })
            else:
                # 整体数据的报告字典，对维修单进行基础性统计，罗列在网页上。所有订单数，未递交数，二次维修数，未核定二次维修原因数等
                elements = MainUtils.elementsnum()

                return render(request, 'crm/maintenance/upload.html', {
                    "index_tag": "crm_maintenance_orders",
                    "elements": elements,

                })
        else:
            report_dic_totag['error'] = "出现了内部错误，请联系管理员"
            # 整体数据的报告字典，对维修单进行基础性统计，罗列在网页上。所有订单数，未递交数，二次维修数，未核定二次维修原因数等
            elements = MainUtils.elementsnum()

            return render(request, 'crm/maintenance/upload.html', {
                "index_tag": "crm_maintenance_orders",
                "report_dic_totag": report_dic_totag,
                "elements": elements,
            })


class MaintenanceWorkList(LoginRequiredMixin, View):
    QUERY_FIELD = ["maintenance_order_id", "shop", "appraisal", "finish_time", "buyer_nick", "sender_mobile",
                   "goods_type", "goods_name", "completer", "is_guarantee", "handling_status", "repeat_tag",
                   "machine_sn", "creator", "create_time", "id"]

    def get(self, request: object) -> object:
        num = request.GET.get("num", 10)
        num = int(num)
        download_tag = request.GET.get("download_tag", None)

        if num > 50:
            num = 50
        # 提取所有未处理的二次维修记录的订单的机器sn。
        orders_repeat = MaintenanceHandlingInfo.objects.filter(repeat_tag=1).values("machine_sn")

        # 取出未处理的二次维修记录的机器sn。
        sns_repeat = []
        for sn in orders_repeat:
            sns_repeat.append(sn['machine_sn'])

        # 根据机器sn，对二次维修的订单的相关订单进行提取。
        all_orders = MaintenanceHandlingInfo.objects.filter(machine_sn__in=sns_repeat).values(
            *self.__class__.QUERY_FIELD).all().order_by("machine_sn", "finish_time")
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

        return render(request, "crm/maintenance/repeatlist.html", {
            "all_orders": order,
            "index_tag": "crm_maintenance_orders",
            "num": str(num),
        })

    def post(self, request):
        order_id = request.POST.get('id')
        department = request.POST.get("department")
        try:
            service_orders = MaintenanceHandlingInfo.objects.all().filter(id=int(order_id))
        except MaintenanceHandlingInfo.DoesNotExist:
            return HttpResponse('{"status": "fail"}', content_type='application/json')
        for service_order in service_orders:
            service_order.repeat_tag = department
            service_order.save()
        return HttpResponse('{"status": "success"}', content_type='application/json')


# class MaintenanceToSN(LoginRequiredMixin, View):
#     QUERY_FIELD = ['machine_sn', 'appraisal', 'finish_time', ]
#
#     def post(self, request):
#         # 定义递交工作台订单的报告字典，以及整体的数据的报告字典
#         report_dic_tosn = {"successful": 0, "ori_successful": 0, "false": 0, "ori_order_error": 0, "repeat_num": 0,
#                              "error": [], "discard": 0}
#         command_id = request.POST.get("tosn", None)
#
#         creator = request.user.username
#
#         if command_id == '1':
#             while True:
#                 pending_orders = MaintenanceHandlingInfo.objects.filter(tomachinesn_status=0)[0:50]
#                 if len(pending_orders) == 0:
#                     break
#                 # # 获取到对应的sn列表，进行列表查询
#                 # sn_list = []
#                 # for order in pending_orders:
#                 #     # 创建一个工作台订单对象，
#                 #     if re.match(r'^[0-9A-Z]+', order.machine_sn):
#                 #         sn_list.append(str(order.machine_sn))
#                 # # 获取到对应sn的批次序列号编码表
#                 # machine_orders = MachineSN.objects.filter(m_sn__in=sn_list)
#                 # 再次循环数据，创建对应的问题编码表
#                 for order in pending_orders:
#                     # 如果没有序列号，则直接抛弃此维修单
#                     if len(order.machine_sn) == 0:
#                         report_dic_tosn['discard'] += 1
#                         try:
#                             order.tomachinesn_status = 3
#                             order.save()
#                             report_dic_tosn['ori_successful'] += 1
#                         except Exception as e:
#                             report_dic_tosn['error'].append(e)
#                             report_dic_tosn['ori_order_error'] += 1
#                         continue
#
#                     faultmachine_order = FaultMachineSN()
#
#                     faultmachine_order.finish_time = order.finish_time
#                     faultmachine_order.appraisal = order.appraisal
#                     faultmachine_order.m_sn = order.machine_sn
#                     faultmachine_order.creator = creator
#
#                     # 验证一下重复值，如果重复，则丢弃数据。
#                     if FaultMachineSN.objects.filter(finish_time=order.finish_time, appraisal=order.appraisal, m_sn=order.machine_sn).exists():
#                         report_dic_tosn['repeat_num'] += 1
#                         try:
#                             order.tomachinesn_status = 1
#                             order.save()
#                             report_dic_tosn['ori_successful'] += 1
#                         except Exception as e:
#                             report_dic_tosn['error'].append(e)
#                             report_dic_tosn['ori_order_error'] += 1
#                         continue
#
#                     machine_order = MachineSN.objects.filter(m_sn=order.machine_sn)
#
#                     if machine_order.count() == 0:
#                         report_dic_tosn['discard'] += 1
#                         try:
#                             order.tomachinesn_status = 2
#                             order.save()
#                             report_dic_tosn['ori_successful'] += 1
#                         except Exception as e:
#                             report_dic_tosn['error'].append(e)
#                             report_dic_tosn['ori_order_error'] += 1
#                         continue
#
#                     faultmachine_order.batch_number = machine_order[0].batch_number
#                     faultmachine_order.goods_id = machine_order[0].goods_id
#                     faultmachine_order.manufactory = machine_order[0].manufactory
#                     faultmachine_order.mfd = machine_order[0].mfd
#
#                     try:
#                         faultmachine_order.save()
#                         report_dic_tosn["successful"] += 1
#                         try:
#                             order.tomachinesn_status = 1
#                             order.save()
#                             report_dic_tosn['ori_successful'] += 1
#                         except Exception as e:
#                             report_dic_tosn['error'].append(e)
#                             report_dic_tosn['ori_order_error'] += 1
#                     except Exception as e:
#                         report_dic_tosn['error'].append(e)
#                         report_dic_tosn['false'] += 1
#
#             # 整体数据的报告字典，对维修单进行基础性统计，罗列在网页上。所有订单数，未递交数，二次维修数，未核定二次维修原因数等
#             elements = MainUtils.elementsnum()
#
#             return render(request, "crm/maintenance/upload.html", {
#                 "index_tag": "crm_maintenance_orders",
#                 "elements": elements,
#                 "report_dic_tosn": report_dic_tosn,
#             })
#
#         else:
#
#             elements = MainUtils.elementsnum()
#             report_dic_tosn['error'] = '请联系管理员，出现了内部错误'
#
#             return render(request, 'crm/maintenance/upload.html', {
#                 "index_tag": "crm_maintenance_orders",
#                 "report_dic_tosn": report_dic_tosn,
#                 "elements": elements,
#             })


class MainUtils(object):
    @staticmethod
    def elementsnum():
        elements = {"total_num": 0, "pending_num": 0, "repeat_num": 0, "unresolved_num": 0, "pending_tosn_num": 0}
        total_num = MaintenanceInfo.objects.all().count()
        pending_num = MaintenanceInfo.objects.filter(towork_status=0).count()

        repeat_num = MaintenanceHandlingInfo.objects.all().count()
        unresolved_num = MaintenanceHandlingInfo.objects.filter(handling_status=0).count()

        pending_tosn_num = MaintenanceHandlingInfo.objects.filter(tomachinesn_status=0).count()
        elements["total_num"] = total_num
        elements["pending_num"] = pending_num
        elements["repeat_num"] = repeat_num
        elements["unresolved_num"] = unresolved_num
        elements["pending_tosn_num"] = pending_tosn_num

        return elements
