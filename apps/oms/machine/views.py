# coding: utf-8

from django.shortcuts import render

# Create your views here.

import csv, datetime, codecs, re, time
from dateutil.relativedelta import relativedelta

from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Q, Sum, Count, Avg, Max, Min
from django.utils.six import moves
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd

from apps.utils.mixin_utils import LoginRequiredMixin

from .forms import UploadFileForm


# class OrderList(LoginRequiredMixin, View):
#     QUERY_FIELD = ['mfd', 'goods_id', 'manufactory', 'order_id', 'quantity', 'msn_segment', 'tosn_status', 'creator', 'create_time']
#
#     def get(self, request):
#         order_tag = request.GET.get("order_tag", "1")
#         search_keywords = request.GET.get("search_keywords", None)
#         num = request.GET.get("num", 10)
#         num = int(num)
#         start_time = request.GET.get("start_time", None)
#         end_time = request.GET.get("end_time", None)
#
#         if num > 50:
#             num = 50
#
#         if search_keywords:
#             all_orders = MachineOrder.objects.filter(
#                 Q(manufactory=search_keywords) | Q(goods_id=search_keywords) | Q(
#                     order_id=search_keywords)
#             )
#         elif start_time and end_time:
#             # 如果查询的是未递交订单，则同时增加一个时间一个维度查询
#             if order_tag == "9":
#                 all_orders = MachineOrder.objects.filter(finish_time__gte=start_time,
#                                                          finish_time__lte=end_time,
#                                                          tosn_status=[1, 2, 3, 4]).order_by("-mfd")
#             # 如果不是查询二次维修订单，则直接一个时间维度查询。
#             else:
#                 all_orders = MachineOrder.objects.filter(finish_time__gte=start_time,
#                                                          finish_time__lte=end_time).order_by("-mfd")
#
#         else:
#             # 如果订单标记为9，则取出所有标记为未递交的订单。
#             if order_tag == "9":
#                 all_orders = MachineOrder.objects.filter(tosn_status=[1, 2, 3, 4]).values(
#                     *self.__class__.QUERY_FIELD).all().order_by("-mfd")
#             else:
#                 all_orders = MachineOrder.objects.values(*self.__class__.QUERY_FIELD).all().order_by(
#                     '-mfd')
#
#         try:
#             page = request.GET.get('page', 1)
#         except PageNotAnInteger:
#             page = 1
#
#         p = Paginator(all_orders, num, request=request)
#         order = p.page(page)
#
#         return render(request, "oms/machine/orderlist.html", {
#             "all_orders": order,
#             "index_tag": "crm_maintenance_orders",
#             "num": str(num),
#             "order_tag": str(order_tag),
#             "start_time": start_time,
#             "end_time": end_time,
#             "search_keywords": search_keywords,
#         })
#
#
# class MachineSNList(LoginRequiredMixin, View):
#     QUERY_FIELD = ['mfd', 'm_sn', 'batch_number', 'manufactory', 'goods_id', 'creator', 'create_time']
#
#     def get(self, request):
#         order_tag = request.GET.get("order_tag", "1")
#         search_keywords = request.GET.get("search_keywords", None)
#         num = request.GET.get("num", 10)
#         num = int(num)
#         start_time = request.GET.get("start_time", None)
#         end_time = request.GET.get("end_time", None)
#
#         if num > 50:
#             num = 50
#
#         if search_keywords:
#             all_orders = MachineSN.objects.filter(
#                 Q(manufactory=search_keywords) | Q(goods_id=search_keywords) | Q(
#                     batch_number=search_keywords)
#             )
#         elif start_time and end_time:
#             # 如果查询的是未递交订单，则同时增加一个时间一个维度查询
#             if order_tag == "9":
#                 all_orders = MachineSN.objects.filter(finish_time__gte=start_time,
#                                                          finish_time__lte=end_time,
#                                                          tosn_status=[1, 2, 3, 4]).order_by("-mfd")
#             # 如果不是未递交订单，则直接一个时间维度查询。
#             else:
#                 all_orders = MachineSN.objects.filter(finish_time__gte=start_time,
#                                                          finish_time__lte=end_time).order_by("-mfd")
#
#         else:
#             # 如果订单标记为9，则取出所有标记为未递交的订单。
#             if order_tag == "9":
#                 all_orders = MachineSN.objects.filter(tosn_status=[1, 2, 3, 4]).values(
#                     *self.__class__.QUERY_FIELD).all().order_by("-mfd")
#             else:
#                 all_orders = MachineSN.objects.values(*self.__class__.QUERY_FIELD).all().order_by(
#                     '-mfd')
#
#         try:
#             page = request.GET.get('page', 1)
#         except PageNotAnInteger:
#             page = 1
#
#         p = Paginator(all_orders, num, request=request)
#         order = p.page(page)
#
#         return render(request, "oms/machine/msnlist.html", {
#             "all_orders": order,
#             "index_tag": "crm_maintenance_orders",
#             "num": str(num),
#             "order_tag": str(order_tag),
#             "start_time": start_time,
#             "end_time": end_time,
#             "search_keywords": search_keywords,
#         })
#
#     pass
#
#
# class OrderUpload(LoginRequiredMixin, View):
#     INIT_FIELDS_DIC = {
#         "序号": "identification",
#         "型号": "goods_id",
#         "工厂": "manufactory",
#         "工厂生产订单号": "order_id",
#         "生产订单数量": "quantity",
#         "要求交期": "mfd",
#         "序列号": "msn_segment",
#     }
#     ALLOWED_EXTENSIONS = ['xls', 'xlsx']
#
#     def get(self, request):
#         elements = {"total_num": 0, "pending_num": 0, "repeat_num": 0, "unresolved_num": 0}
#         total_num = MachineOrder.objects.all().count()
#         pending_num = MachineOrder.objects.filter(tosn_status=0).count()
#
#         elements["total_num"] = total_num
#         elements["pending_num"] = pending_num
#
#         return render(request, "oms/machine/upload.html", {
#             "index_tag": "crm_maintenance_orders",
#             "elements": elements,
#         })
#
#     def post(self, request):
#         elements = {"total_num": 0, "pending_num": 0, "repeat_num": 0, "unresolved_num": 0}
#         creator = request.user.username
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             _result = self.handle_upload_file(request.FILES['file'], creator)
#             # 如果返回的是错误信息，就是字符串格式，直接执行下面的路径
#             if isinstance(_result, str):
#
#                 total_num = MachineOrder.objects.all().count()
#                 pending_num = MachineOrder.objects.filter(tosn_status=0).count()
#
#                 elements["total_num"] = total_num
#                 elements["pending_num"] = pending_num
#
#                 return render(request, "oms/machine/upload.html", {
#                     "messages": _result,
#                     "index_tag": "crm_maintenance_orders",
#                     "elements": elements,
#                 })
#             # 判断是字典的话，就直接返回字典结果到前端页面。
#             elif isinstance(_result, dict):
#
#                 total_num = MachineOrder.objects.all().count()
#                 pending_num = MachineOrder.objects.filter(tosn_status=0).count()
#
#                 elements["total_num"] = total_num
#                 elements["pending_num"] = pending_num
#
#                 return render(request, "oms/machine/upload.html", {
#                     "report_dic": _result,
#                     "index_tag": "crm_maintenance_orders",
#                     "elements": elements,
#                 })
#
#         else:
#             form = UploadFileForm()
#
#         total_num = MachineOrder.objects.all().count()
#         pending_num = MachineOrder.objects.filter(towork_status=0).count()
#
#         elements["total_num"] = total_num
#         elements["pending_num"] = pending_num
#
#         return render(request, "oms/machine/upload.html", {
#             "messages": form,
#             "index_tag": "crm_maintenance_orders",
#             "elements": elements,
#         })
#
#     def handle_upload_file(self, _file, creator):
#         report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
#
#         if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
#             with pd.ExcelFile(_file) as xls:
#                 df = pd.read_excel(xls, sheet_name='Sheet1')
#
#                 # 获取表头，对表头进行转换成数据库字段名
#                 columns_key = df.columns.values.tolist()
#                 for i in range(len(columns_key)):
#                     if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
#                         columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])
#
#                 # 验证一下必要的核心字段是否存在
#                 _ret_verify_field = MachineOrder.verify_mandatory(columns_key)
#                 if _ret_verify_field is not None:
#                     return _ret_verify_field
#
#                 # 更改一下DataFrame的表名称
#                 columns_key_ori = df.columns.values.tolist()
#                 ret_columns_key = dict(zip(columns_key_ori, columns_key))
#                 df.rename(columns=ret_columns_key, inplace=True)
#
#                 num_end = 0
#                 num_step = 300
#                 num_total = len(df)
#
#                 for i in range(1, int(num_total / num_step) + 2):
#                     num_start = num_end
#                     num_end = num_step * i
#                     intermediate_df = df.iloc[num_start: num_end]
#
#                     # 获取导入表格的字典，每一行一个字典。这个字典最后显示是个list
#                     _ret_list = intermediate_df.to_dict(orient='records')
#                     intermediate_report_dic = self.save_resources(_ret_list, creator)
#                     for k, v in intermediate_report_dic.items():
#                         if k == "error":
#                             if intermediate_report_dic["error"]:
#                                 report_dic[k].append(v)
#                         else:
#                             report_dic[k] += v
#                 return report_dic
#
#         # 以下是csv处理逻辑，和上面的处理逻辑基本一致。
#         elif '.' in _file.name and _file.name.rsplit('.')[-1] == 'csv':
#             df = pd.read_csv(_file, encoding="GBK", chunksize=300)
#
#             for piece in df:
#                 columns_key = piece.columns.values.tolist()
#                 for i in range(len(columns_key)):
#                     if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
#                         columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])
#                 _ret_verify_field = MachineOrder.verify_mandatory(columns_key)
#                 if _ret_verify_field is not None:
#                     return _ret_verify_field
#                 columns_key_ori = piece.columns.values.tolist()
#                 ret_columns_key = dict(zip(columns_key_ori, columns_key))
#                 piece.rename(columns=ret_columns_key, inplace=True)
#                 _ret_list = piece.to_dict(orient='records')
#                 intermediate_report_dic = self.save_resources(_ret_list, creator)
#                 for k, v in intermediate_report_dic.items():
#                     if k == "error":
#                         if intermediate_report_dic["error"]:
#                             report_dic[k].append(v)
#                     else:
#                         report_dic[k] += v
#             return report_dic
#
#         else:
#             return "只支持excel和csv文件格式！"
#
#     def save_resources(self, resource, creator):
#         # 设置初始报告
#         report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
#
#         # 开始导入数据
#         for row in resource:
#             # ERP导出文档添加了等于号，毙掉等于号。
#             order = MachineOrder()  # 创建表格每一行为一个对象
#             for k, v in row.items():
#                 if re.match(r'^=', str(v)):
#                     row[k] = v.replace('=', '').replace('"', '')
#
#             mfd = str(row["mfd"])
#             msn_segment = str(row["msn_segment"])
#             identification = int(row["identification"])
#
#             # 状态是取消的订单，就舍弃
#             if '取消订单' in mfd:
#                 report_dic["discard"] += 1
#                 continue
#
#             if len(msn_segment) < 15 and "-" in msn_segment:
#                 report_dic["discard"] += 1
#                 continue
#
#             if "-" not in msn_segment:
#                 report_dic["discard"] += 1
#                 report_dic["error"].append("%s行序列号段连接字符错误" % (row["identification"]))
#                 continue
#
#             # 如果订单号查询，已经存在，丢弃订单，计数为重复订单
#             elif MachineOrder.objects.filter(identification=identification).exists():
#                 report_dic["repeated"] += 1
#                 continue
#
#             for k, v in row.items():
#
#                 # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
#                 if hasattr(order, k):
#                     if str(v) in ['nan', 'NaT']:
#                         pass
#                     else:
#                         setattr(order, k, v)  # 更新对象属性为字典对应键值
#             try:
#                 order.creator = creator
#                 order.save()
#                 report_dic["successful"] += 1
#             # 保存出错，直接错误条数计数加一。
#             except Exception as e:
#                 report_dic["error"].append(e)
#                 report_dic["false"] += 1
#         return report_dic
#
#
# class ToMachineSN(LoginRequiredMixin, View):
#
#     def post(self, request):
#         report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "create_suc": 0, "create_false": 0 ,"error": [], "create_error": []}
#         tomachinesn = str(request.POST.get("tomachinesn", None))
#         if tomachinesn == '1':
#             while True:
#                 all_orders = MachineOrder.objects.filter(tosn_status=0)[0:30]
#                 if len(all_orders) == 0:
#                     break
#                 print(all_orders)
#                 for order in all_orders:
#                     start_num, end_num = order.msn_segment.split('-')[0], order.msn_segment.split('-')[1]
#                     if re.match(r'^[0-9]+$', start_num):
#                         start_num = int(start_num)
#                         end_num = int(end_num)
#                         while start_num <= end_num:
#                             machinesn = MachineSN()
#                             machinesn.mfd = order.mfd
#                             machinesn.batch_number = order.order_id
#                             machinesn.manufactory = order.manufactory
#                             machinesn.goods_id = order.goods_id
#                             machinesn.m_sn = start_num
#                             try:
#                                 machinesn.save()
#                                 report_dic["create_suc"] += 1
#                             except Exception as e:
#                                 report_dic["create_error"].append(e)
#                                 report_dic["create_false"] += 1
#                             start_num += 1
#
#                     elif re.match(r'^[0-9A-Za-z]+$', start_num):
#                         batch_number = start_num[:11]
#                         start_num = int(start_num[-5:]) + 100000
#                         end_num = int(end_num[-5:]) + 100000
#                         while start_num <= end_num:
#                             machinesn = MachineSN()
#                             machinesn.mfd = order.mfd
#                             machinesn.batch_number = batch_number
#                             machinesn.manufactory = order.manufactory
#                             machinesn.goods_id = order.goods_id
#                             machinesn.m_sn = batch_number + str(start_num)[-5:]
#                             try:
#                                 machinesn.save()
#                                 report_dic["create_suc"] += 1
#                             except Exception as e:
#                                 report_dic["create_false"] += 1
#                             start_num += 1
#
#                     else:
#                         report_dic["discard"] += 1
#                     order.tosn_status = 1
#                     try:
#                         order.save()
#                         report_dic["successful"] += 1
#                     except Exception as e:
#                         report_dic["error"].append(e)
#                         report_dic["false"] += 1
#             print(report_dic)
#             elements = {"total_num": 0, "pending_num": 0, "repeat_num": 0, "unresolved_num": 0}
#             total_num = MachineOrder.objects.all().count()
#             pending_num = MachineOrder.objects.filter(tosn_status=0).count()
#
#             elements["total_num"] = total_num
#             elements["pending_num"] = pending_num
#
#             return render(request, "oms/machine/upload.html", {
#                 "index_tag": "oms_machine_upload",
#                 "report_dic_towork": report_dic,
#                 "elements": elements,
#             })
#         else:
#             elements = {"total_num": 0, "pending_num": 0, "repeat_num": 0, "unresolved_num": 0}
#             total_num = MachineOrder.objects.all().count()
#             pending_num = MachineOrder.objects.filter(tosn_status=0).count()
#
#             elements["total_num"] = total_num
#             elements["pending_num"] = pending_num
#
#             return render(request, "oms/machine/upload.html", {
#                 "index_tag": "oms_machine_upload",
#                 "elements": elements,
#             })
#
#
# class ToSummary(LoginRequiredMixin, View):
#     def post(self, request):
#         report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "create_suc": 0, "create_false": 0,
#                       "error": [], "create_error": []}
#         dateformat = "%Y-%m"
#         tosummary_tag = request.POST.get("tosummary_tag", None)
#         products_list = {}
#         products_fault_list = {}
#
#         if tosummary_tag == '1':
#             # 找到统计表中的最后统计时间
#             last_time = GoodFaultSummary.objects.all().aggregate(Max('statistic_time'))
#             # 如果不存在
#             if last_time["statistic_time__max"] is None:
#                 # 初始化第一个月的开始时间是工厂订单时间。
#                 _pre_start_time = MachineOrder.objects.all().aggregate(Min("mfd"))["mfd__min"]
#                 # 对起始时间进行处理，修正到对应年度月份的一号
#                 start_time = datetime.datetime(_pre_start_time.year, _pre_start_time.month, 1, 0, 0, 0)
#                 start_month = start_time.strftime("%Y-%m")
#
#                 _pre_goods_initial = MachineOrder.objects.extra(where=['date_format(mfd, "%s") = "%s"'],
#                                                                 params=[dateformat, start_month]).values(
#                     "goods_id").annotate(quantity=Sum("quantity")).values("goods_id", "quantity")
#                 # 循环创建初始化字典，初始化数量为0
#
#                 for goods_id in _pre_goods_initial:
#                     products_list[goods_id["goods_id"]] = 0
#                     products_fault_list[goods_id["goods_id"]] = 0
#             else:
#                 # 如果已经存在统计时间，则从最大的时间作为开始进行统计
#                 _pre_start_time = last_time["statistic_time__max"]
#                 start_time = datetime.datetime(_pre_start_time.year, _pre_start_time.month, 1, 0, 0, 0)
#                 start_month = start_time.strftime( "%Y-%m")
#
#                 _pre_goods_initial = GoodFaultSummary.objects.all().filter(statistic_time=start_month)
#
#                 # 循环创建初始化字典，初始化数量为最后统计时间的累积量
#                 for goods_id in _pre_goods_initial:
#                     products_list[goods_id["goods_id"]] = goods_id.production_cumulation
#                     products_fault_list[goods_id["goods_id"]] = goods_id.fault_cumulation
#
#             # 截止统计时间是当前月的1号
#             end_time = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1, 0, 0, 0)
#             # 开始进行大循环
#             while start_time < end_time:
#                 start_month = start_time.strftime("%Y-%m")
#
#                 # 通过扩展查询以月度为聚合统计数，where后面跟表达式，param后面跟对应表达式中的参数。
#                 goods_production = MachineOrder.objects.extra(where=['date_format(mfd, "%s") = "%s"'],
#                                                               params=[dateformat, start_month]).values(
#                     "goods_id").annotate(quantity=Sum("quantity")).values("goods_id", "quantity")
#
#                 goods_fault = FaultMachineSN.objects.extra(where=['date_format(finish_time, "%s") = "%s"'],
#                                                            params=[dateformat, start_month]).values(
#                     "goods_id").annotate(quantity=Count("id")).values("goods_id", "quantity")
#
#                 for goods_id in products_list:
#                     goodfaultsummary = GoodFaultSummary()
#                     production_quantity = goods_production.filter(goods_id=goods_id)
#                     print(production_quantity)
#
#                 # 对时间进行月度增加，就需要用到，dateutil.relativedelta，直接用datetime.tiemdelta无法对月度直接增加。只能增加天数
#                 start_month = start_month + relativedelta(months=+1)
#
#
#
#
#
#
#
#
#
#             object_month = last_month.strftime("%Y-%m")
#
#
#
#
#             print(goods_production)
#             for i in goods_fault:
#                 print(i)
#             for i in goods_production:
#                 print(i)
#
#
#         pass
#
#
# class ToFaultSummary(LoginRequiredMixin, View):
#     pass