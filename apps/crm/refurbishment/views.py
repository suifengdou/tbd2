# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 9:19
# @Author  : Hann
# @Site    :
# @File    : views.py
# @Software: PyCharm

import datetime, csv, datetime, codecs, re, time
from dateutil.relativedelta import relativedelta

from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http import HttpResponse, StreamingHttpResponse
# from .forms import UploadFileForm
from django.db.models import Q, Sum, Count, Avg, Max, Min
from django.utils.six import moves
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd



from .models import OriRefurbishInfo, RefurbishInfo, ApprasialInfo, RefurbishTechSummary, RefurbishGoodSummary

from apps.utils.mixin_utils import LoginRequiredMixin


class RefurbishTask(LoginRequiredMixin, View):

    def get(self, request):
        elements = RefurbishUtils.get_informations()

        return render(request, 'crm/refurbishment/upload.html', {
            "elements": elements,

        })

    def post(self, request):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        towork = request.POST.get("towork", None)
        # 把手工登记单，递交到翻新单列表中。
        if towork == '1':
            # 大循环，考虑系统资源等问题，每次递交50单
            while True:
                all_orders = OriRefurbishInfo.objects.all().filter(submit_tag=0)[0:50]
                orders_num = all_orders.count()
                # 判断一下最后取出来的数量。当没有订单的时候，结束循环
                if orders_num == 0:
                    break
                for order in all_orders:
                    refurbish = RefurbishInfo()
                    # 前置sn码进行验证
                    pre_sn = str(order.pre_sn)
                    # 等于4的时候，按照新编码规则内容处理。
                    if len(pre_sn) == 4:
                        mid_batch = str(order.mid_batch)
                        tail_sn = str(order.tail_sn)
                        goods_number = str(order.goods_name.goods_number)
                        category = str(order.goods_name.category)
                        m_sn = pre_sn + category + goods_number + mid_batch + tail_sn
                    # 大于4的时候，按照老编码规则内容处理。
                    elif len(pre_sn) > 4:
                        m_sn = pre_sn
                    # 出现小于4或其他情况时候，进行异常处理，保存错误，跳过此循环。
                    else:
                        report_dic["false"] += 1
                        report_dic['error'].append("%s 前置单号错误"%order.pre_sn)
                        try:
                            order.submit_tag = 3
                            order.save()
                        except Exception as e:
                            report_dic["error"].append(e)
                        continue
                    # 判断此机器sn是否已经存在，如果存在则舍去，标记为重复值。跳出此循环
                    standard_time = order.ref_time - relativedelta(days=1)
                    current_time = order.ref_time.strftime("%Y-%m-%d")
                    repeat_tag = RefurbishInfo.objects.all().filter(m_sn=m_sn, ref_time__gte=standard_time).values("ref_time")
                    if repeat_tag.exists():
                        last_time = repeat_tag[0]["ref_time"].strftime("%Y-%m-%d")
                        if current_time == last_time:
                            report_dic["repeated"] += 1
                            try:
                                order.submit_tag = 2
                                order.save()
                            except Exception as e:
                                report_dic["error"].append(e)
                            continue
                    # 进行机器sn的验证，查看sn是否符合规则。
                    if len(m_sn) not in [16, 8]:
                        report_dic["false"] += 1
                        report_dic['error'].append('%s 序列号验证错误' % m_sn)
                        try:
                            order.submit_tag = 3
                            order.save()
                        except Exception as e:
                            report_dic["error"].append(e)
                        continue
                    if order.new_sn:
                        refurbish.memo = str(order.new_sn)
                    refurbish.m_sn = m_sn
                    refurbish.technician = str(order.created_by.username)
                    refurbish.appraisal = str(order.appraisal.appraisal)
                    refurbish.ref_time = current_time
                    refurbish.goods_name = str(order.goods_name.goods_name)
                    refurbish.goods_id = str(order.goods_name.goods_id)
                    refurbish.creator = str(request.user.username)

                    try:
                        refurbish.save()
                        try:
                            order.submit_tag = 1
                            report_dic["successful"] += 1
                            order.save()
                        except Exception as e:
                            report_dic["false"] += 1
                            report_dic["error"].append(e)
                            order.submit_tag = 3
                            order.save()
                    except Exception as e:
                        report_dic["false"] +=1
                        report_dic["error"].append(e)
                        order.submit_tag = 3
                        order.save()
        # 翻新单列表进行统计
        elif towork == '2':
            start_time = RefurbishInfo.objects.all().filter(summary_tag=0).aggregate(Min("ref_time"))
            end_time = RefurbishInfo.objects.all().filter(summary_tag=0).aggregate(Max("ref_time"))
            dateformat = "%Y-%m-%d"
            if start_time["ref_time__min"] is not None:
                pre_start_time = start_time["ref_time__min"]
                pre_end_time = end_time["ref_time__max"]
                start_time = datetime.datetime(pre_start_time.year, pre_start_time.month, pre_start_time.day, 0, 0, 0)
                end_time = datetime.datetime(pre_end_time.year, pre_end_time.month, pre_end_time.day, 0, 0, 0) + relativedelta(days=1)
                while start_time < end_time:
                    current_time = start_time.strftime("%Y-%m-%d")
                    _pre_data_summary = RefurbishInfo.objects.all().extra(where=['summary_tag=0 and date_format(ref_time, "%s")="%s"'], params=[dateformat, current_time])
                    _pre_technician_summary = _pre_data_summary.values("technician").annotate(quantity=Count("m_sn")).values("technician", "quantity")
                    _pre_goods_summary = _pre_data_summary.values("goods_id", "goods_name").annotate(quantity=Count("m_sn")).values("goods_name", "goods_id", "quantity")
                    mission_tag = 0
                    # 统计技术员的工作量
                    for technician in _pre_technician_summary:
                        if RefurbishTechSummary.objects.filter(statistical_time=current_time,technician=technician["technician"]).exists():
                            report_dic["error"].append("%s同学的%s已经统计过了，需要查看异常订单"%(technician.technician, current_time))
                            report_dic["repeated"] += 1
                            mission_tag += 1
                            continue
                        refurbishtech = RefurbishTechSummary()
                        refurbishtech.statistical_time = datetime.datetime(start_time.year, start_time.month, start_time.day, 10, 0, 0)
                        refurbishtech.technician = technician["technician"]
                        refurbishtech.quantity = technician["quantity"]
                        refurbishtech.creator = request.user.username
                        try:
                            refurbishtech.save()
                        except Exception as e:
                            report_dic["error"].append(e)
                            mission_tag += 1

                    # 统计机器维度的数量
                    for goods in _pre_goods_summary:
                        if RefurbishGoodSummary.objects.filter(statistical_time=current_time, goods_id=goods["goods_id"]).exists():
                            report_dic["error"].append("%s型号的%s已经统计过了，需要查看异常订单" % (goods["goods_id"], current_time))
                            report_dic["repeated"] += 1
                            mission_tag += 1
                            continue
                        refurbishgoods = RefurbishGoodSummary()
                        refurbishgoods.statistical_time = datetime.datetime(start_time.year, start_time.month, start_time.day, 10, 0, 0)
                        refurbishgoods.goods_name = goods["goods_name"]
                        refurbishgoods.goods_id = goods["goods_id"]
                        refurbishgoods.quantity = goods["quantity"]
                        refurbishgoods.creator = request.user.username
                        try:
                            refurbishgoods.save()
                        except Exception as e:
                            report_dic["error"].append(e)
                            mission_tag += 1
                    # 根据错误信息进行判断，如果统计异常，会进行批量异常标记，防止出现统计错误的情况。
                    if mission_tag == 0:
                        for order in _pre_data_summary:
                            order.summary_tag = 1
                            order.save()
                        report_dic["successful"] += 1
                    else:
                        for order in _pre_data_summary:
                            order.summary_tag = 3
                            order.save()
                        report_dic["false"] += 1
                    start_time = start_time + relativedelta(days=1)

        elements = RefurbishUtils.get_informations()
        return render(request, 'crm/refurbishment/upload.html', {
            "elements": elements,
            "report_dic": report_dic,
        })


class RefurbishOverView(LoginRequiredMixin, View):
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
                # 计算一下时间间隔，是否是两个月内。如果超出或者选择错误。
                if d_value.days in range(1, 61):
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
        elements = {"index_tag": "crm_refurbishment_overview"}
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

        pre_tech_summary = RefurbishTechSummary.objects.all().filter(
            statistical_time__gte=datetime.datetime.strptime(confirm_data["start_time"], "%Y-%m-%d %H:%M:%S"),
            statistical_time__lte=datetime.datetime.strptime(confirm_data["end_time"], "%Y-%m-%d %H:%M:%S"))
        tech_days = pre_tech_summary.values("statistical_time", "technician").annotate(quantity=Sum("quantity")).values("statistical_time", "technician", "quantity").order_by("statistical_time")
        tech_summary = pre_tech_summary.values("technician").annotate(quantity=Sum("quantity")).values("technician", "quantity").order_by("-quantity")

        # 首先计算出百分比堆叠图的时间列表。汇总到一个列表中。进行统计初始化。
        days_list_display = []
        technicians_data_display = []
        days_list = []
        technicians = []
        # 先对统计时间进行统计，技术员进行统计
        for day in tech_days:
            current_day = day["statistical_time"].strftime("%Y-%m-%d")
            # 记录一次统计时间的显示时间格式，统计一次下面数据循环需要用到的时间格式
            if current_day not in days_list_display:
                days_list_display.append(str(current_day))
                days_list.append(day["statistical_time"])
            # 对维修员进行统计
            if day["technician"] not in technicians:
                technicians.append(day["technician"])
        # 对维修员进行循环统计
        for tech in technicians:
            technicians_data = {"name": tech, "data": []}
            # 对统计时间进行循环。
            for current_day in days_list:
                quantity = tech_days.filter(technician=tech, statistical_time=current_day)
                # 判断时间是否存在，如果存在，就保存存在的数量。如果不存在，就为0
                if quantity.exists():
                    technicians_data["data"].append(quantity[0]["quantity"])
                else:
                    technicians_data["data"].append(0)
            # 维修员的维修数据进行列表汇总
            technicians_data_display.append(technicians_data)
        # 维修员每天的维修数据
        m_total["days_list_display"] = days_list_display
        m_total["technicians_data_display"] = technicians_data_display

        # 对维修员进行排序
        techs_sort = []
        for tech in tech_summary:
            tech_data = [tech["technician"], tech["quantity"]]
            techs_sort.append(tech_data)
        m_total["techs_sort"] = techs_sort

        pre_goods_summary = RefurbishGoodSummary.objects.all().filter(
            statistical_time__gte=datetime.datetime.strptime(confirm_data["start_time"], "%Y-%m-%d %H:%M:%S"),
            statistical_time__lte=datetime.datetime.strptime(confirm_data["end_time"], "%Y-%m-%d %H:%M:%S"))

        goods_summary = pre_goods_summary.values("goods_name").annotate(quantity=Sum("quantity")).values("goods_name", "quantity").order_by("-quantity")
        goods_sort = []
        for good in goods_summary:
            good_data = [good["goods_name"], good["quantity"]]
            goods_sort.append(good_data)

        m_total["goods_sort"] = goods_sort

        return render(request, 'crm/refurbishment/overview.html', {
            "elements": elements,
            "m_total": m_total,
        })


class RefurbishUtils(object):
    @staticmethod
    def get_informations():
        elements = {"index_tag": "crm_refurbishment_task", "pending_num": 0, "total_num": 0,"refurbish_num": 0, "unsummary_num": 0}
        total_num = OriRefurbishInfo.objects.all().count()
        pending_num = OriRefurbishInfo.objects.filter(submit_tag=0).count()
        refurbish_num = RefurbishInfo.objects.all().count()
        unsummary_num = RefurbishInfo.objects.filter(summary_tag=0).count()

        elements["total_num"] = total_num
        elements["pending_num"] = pending_num
        elements["refurbish_num"] = refurbish_num
        elements["unsummary_num"] = unsummary_num
        return elements

