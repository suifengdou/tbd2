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
# from .forms import UploadFileForm
from django.db.models import Q
from django.utils.six import moves
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd


from .models import OrderInfo
from apps.crm.customers.models import CustomerInfo, CustomerTendency
from .forms import ToCustomerNum, UploadFileForm


class OrderList(View):
    QUERY_FIELD = ["shop", "order_time", "receiver_name", "receiver_address", "receiver_mobile",
                   "payment", "goods_id", "goods_name", "real_quantity", "allocated_total_fee"]

    def get(self, request: object) -> object:
        order_tag = request.GET.get("order_tag", '1')
        search_keywords = request.GET.get("search_keywords", None)
        num = request.GET.get("num", 10)
        num = int(num)
        download_tag = request.GET.get("download_tag", None)

        if num > 50:
            num = 50

        if search_keywords:
            all_orders = OrderInfo.objects.filter(
                Q(receiver_mobile=search_keywords) | Q(sub_original_order_id=search_keywords) | Q(invoice_no=search_keywords)
            )
        else:

            if order_tag == '0':
                all_orders = OrderInfo.objects.filter(tocustomer_status=str(0)).values(
                    *self.__class__.QUERY_FIELD).all().order_by('-create_time')
            else:
                all_orders = OrderInfo.objects.values(*self.__class__.QUERY_FIELD).all().order_by('-create_time')

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orders, num, request=request)
        order = p.page(page)

        if download_tag:
            if all_orders.count() > 5000:
                return render(request, "crm/orders/orderlist.html", {
                    "all_orders": order,
                    "index_tag": "crm_orders",
                    "num": str(num),
                    "order_tag": str(order_tag),
                    "download_error": "订单数量最多导出5000单",
                })

            # 导出文件取名
            now = datetime.datetime.now()
            now = str(now)
            name = now.replace(':', '')

            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="{}.csv"'.format(name)

            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)
            writer.writerow(['店铺', '交易时间', '收件人', '收货地址', '收件人手机', '订单支付金额', '货品编号', '货品名称',
                             '实发数量', '分摊后总价', "生成客户信息状态"])
            for order in all_orders:
                writer.writerow(
                    [order['shop'], order['order_time'], order['receiver_name'], order['receiver_address'],
                     order['receiver_mobile'], order['payment'], order['goods_id'], order['goods_name'],
                     order['real_quantity'], order['allocated_total_fee']])
            return response

        return render(request, "crm/orders/orderlist.html", {
            "all_orders": order,
            "index_tag": "crm_orders",
            "num": str(num),
            "order_tag": str(order_tag)
        })

    def post(self, request):
        pass


class OrderUpload(View):
    INIT_FIELDS_DIC = {
        "订单编号": "erp_order_id",
        "店铺": "shop",
        "订单来源": "order_source",
        "仓库": "warehouse",
        "子单原始单号": "sub_original_order_id",
        "订单状态": "status",
        "订单类型": "order_type",
        "货到付款": "cash_on_delivery",
        "订单退款状态": "refund_status",
        "交易时间": "order_time",
        "付款时间": "pay_time",
        "客户网名": "buyer_nick",
        "收件人": "receiver_name",
        "收货地区": "receiver_area",
        "收货地址": "receiver_address",
        "收件人手机": "receiver_mobile",
        "分销商": "distributor",
        "来源组合装编号": "discreteness_source_id",
        "收件人电话": "receiver_telephone",
        "邮编": "zip_code",
        "区域": "order_area",
        "物流公司": "logistics_company",
        "物流单号": "invoice_no",
        "买家留言": "buyer_message",
        "客服备注": "seller_remark",
        "打印备注": "print_remark",
        "订单支付金额": "payment",
        "邮费": "post_fee",
        "订单总优惠": "discount_fee",
        "应收金额": "total_fee",
        "款到发货金额": "payment_and_delivery_fee",
        "货到付款金额": "cod_fee",
        "预估重量": "weight",
        "需要发票": "has_invoice",
        "发票抬头": "invoice_rise",
        "发票内容": "invoice_content",
        "业务员": "salesman",
        "审核人": "auditor",
        "商家编码": "goods_id",
        "货品编号": "goods_code",
        "货品名称": "goods_name",
        "规格名称": "goods_specification",
        "平台货品名称": "platform_goods_name",
        "平台规格名称": "platform_goods_specification",
        "下单数量": "quantity",
        "标价": "fixed",
        "货品总优惠": "goods_discount_fee",
        "成交价": "goods_price",
        "分摊后价格": "allocated_price",
        "打折比": "discount_ratio",
        "实发数量": "real_quantity",
        "分摊后总价": "allocated_total_fee",
        "退款前支付金额": "before_refund_payment",
        "分摊邮费": "allocated_post_fee",
        "单品支付金额": "goods_payment",
        "拆自组合装": "discreteness_id",
        "赠品方式": "gift_type"
    }
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    def get(self, request: object) -> object:

        return render(request, "crm/orders/upload.html", {
            "index_tag": "crm_orders",
        })

    def post(self, request):

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            _result = self.handle_upload_file(request.FILES['file'])
            # 如果返回的是错误信息，就是字符串格式，直接执行下面的路径
            if isinstance(_result, str):
                return render(request, "crm/orders/upload.html", {
                    "messages": _result,
                    "index_tag": "crm_orders",
                })
            # 判断是字典的话，就直接返回字典结果到前端页面。
            elif isinstance(_result, dict):
                return render(request, "crm/orders/upload.html", {
                    "report_dic": _result,
                    "index_tag": "crm_orders",
                })

        else:
            form = UploadFileForm()
        return render(request, "crm/orders/upload.html", {
            "messages": form,
            "index_tag": "crm_orders",
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
                _ret_verify_field = OrderInfo.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field

                # 更改一下DataFrame的表名称
                columns_key_ori = df.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                df.rename(columns=ret_columns_key, inplace=True)

                num_end = 0
                num_step = 300
                num_total = len(df)

                for i in range(1, int(num_total/num_step)+2):
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
                _ret_verify_field = OrderInfo.verify_mandatory(columns_key)
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

        platform_pre = {
            'tianheyi88': '淘宝',
            '小狗电器自营店': '淘宝',
            '小狗电器旗舰店': '淘宝',
            '小狗京东商城店铺FBP': '京东FBP',
            '小狗蓝弧专卖店': '淘宝',
            '小狗香橙专卖店': '淘宝',
            '小狗官方商城': '官方商城',
            '小狗电器微信旗舰店': '微信小程序',
            '微小店': '微信小程序',
            '小狗品牌集市店': '淘宝',
            '小狗生活集市店': '淘宝',
            '小狗蓝弧专卖店供应商': '淘宝',
            '村淘小狗商家': '淘宝',
            '小狗萌店': '微信小程序',
            '拼多多小狗香橙': '拼多多',
            '小狗微小店': '微信小程序',
            '官方微信小程序': '微信小程序',
            'puppy旗舰店': '淘宝'
        }

        # 开始导入数据
        for row in resource:
            # ERP导出文档添加了等于号，毙掉等于号。
            order = OrderInfo()  # 创建表格每一行为一个对象
            for k, v in row.items():
                if re.match(r'^=', str(v)):
                    row[k] = v.replace('=', '').replace('"', '')

            receiver_mobile = str(row["receiver_mobile"])
            sub_original_order_id = str(row['sub_original_order_id'])
            erp_order_id = str(row["erp_order_id"])
            goods_id = str(row['goods_id'])

            # 如果手机为空，就丢弃这个订单，计数为丢弃订单
            if re.match(r'^[0-9VW]', receiver_mobile) is None:
                report_dic["discard"] += 1
                continue

            # 如果订单号，子订单原始单号，货品名称三个维度查询，已经存在，丢弃订单，计数为重复订单
            elif OrderInfo.objects.filter(erp_order_id=erp_order_id, sub_original_order_id=sub_original_order_id,
                                          goods_id=goods_id).exists():
                report_dic["repeated"] += 1
                continue

            elif len(str(row['seller_remark'])) > 500:
                row['seller_remark'] = row['seller_remark'][0:499]

            elif len(str(row['goods_specification'])) > 30:
                row['goods_specification'] = row['goods_specification'][0:29]

            # 根据店铺查找对应的平台，设置对应的平台。
            elif platform_pre.get(row['shop'], None) is not None:
                order.platform = platform_pre[row['shop']]

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


class OrderOperate(View):
    pass


class OrderOverview(View):
    tocustomers_num_obj = ToCustomerNum()

    def get(self, request: object) -> object:

        return render(request, 'crm/orders/overview.html', {
            "tocustomers_num_obj": self.__class__.tocustomers_num_obj,
            "index_tag": "crm_orders",

        })


class OrderToCustomer(View):

    tocustomers_num_obj = ToCustomerNum()

    def get(self, request: object) -> object:
        pending_num = OrderInfo.objects.filter(tocustomer_status=str(0)).count()
        return render(request, 'crm/orders/overview-tc.html', {
            "index_tag": "crm_orders",
            'tocustomers_num_obj': self.__class__.tocustomers_num_obj,
            "pending_num": pending_num,
        })

    def post(self, request):
        tocustomer_input_obj = ToCustomerNum(request.POST)
        if tocustomer_input_obj.is_valid():
            # 操作导入
            num = int(request.POST.get("num"))
            report_dic = self.ctsloopbody(num)
            pending_num = OrderInfo.objects.filter(tocustomer_status=str(0)).count()
            return render(request, 'crm/orders/overview-tc.html', {
                "index_tag": "crm_orders",
                'tocustomers_num_obj': self.__class__.tocustomers_num_obj,
                "report_dic": report_dic,
                "pending_num": pending_num,
            })
        else:
            # 出错反馈问题原因
            tocustomers_errors = tocustomer_input_obj.errors
            pending_num = OrderInfo.objects.filter(tocustomer_status=str(0)).count()
            return render(request, 'crm/orders/overview-tc.html', {
                "index_tag": "crm_orders",
                'tocustomers_num_obj': self.__class__.tocustomers_num_obj,
                'tocustomers_errors': tocustomers_errors,
                "pending_num": pending_num,
            })

    def ctsloopbody(self, num):

        report_dic = {"create_cus_success": 0, "create_cus_fail": 0, "order_success": 0, "order_fail": 0,
                      "error_area": 0, "discard": 0, "update_cus_success": 0, "update_cus_fail": 0}

        num_step = 300

        if num > num_step:
            modulo_num = int(num) % num_step
            div_num = int(int(num) / num_step)

            orders = OrderInfo.objects.filter(tocustomer_status=str(0)).all()[: modulo_num]
            intermediate_report_dic = self.ctstidy(orders)
            for k, v in intermediate_report_dic.items():
                report_dic[k] += v


            # 开始大循环
            for i in range(1, int(div_num) + 1):

                orders = OrderInfo.objects.filter(tocustomer_status=str(0)).all()[: num_step]

                intermediate_report_dic = self.ctstidy(orders)

                for k, v in intermediate_report_dic.items():
                    report_dic[k] += v

        else:
            orders = OrderInfo.objects.filter(tocustomer_status=str(0)).all()[: num]
            intermediate_report_dic = self.ctstidy(orders)
            for k, v in intermediate_report_dic.items():
                report_dic[k] += v
        return report_dic

    def ctstidy(self, iterms):

        report_dic = {"create_cus_success": 0, "create_cus_fail": 0, "order_success": 0, "order_fail": 0,
                      "error_area": 0, "discard": 0, "update_cus_success": 0, "update_cus_fail": 0}
        # 开始小循环
        for order in iterms:

            # 对电话进行验证，如果电话不存在，就直接舍弃这个客户信息。没有手机的客户创建之后无法维护。以手机为标准识别字段。
            if re.match(r'\d+', str(order.receiver_mobile)) is None:
                report_dic['discard'] += 1
                # 保存特殊状态
                order.tocustomer_status = 2
                order.save()

            # 如果客户信息已经存在客户系统中，逻辑操作。
            if CustomerInfo.objects.filter(mobile=order.receiver_mobile).exists():
                intermediate_report_dic = self.updatecustomer(order)

                for k, v in intermediate_report_dic.items():
                    report_dic[k] += v
            # 如果客户信息不存在客户系统中，进行创建客户信息的操作。
            else:
                # 创建一个客户信息的对象
                # 保存客户基本信息，准备创建客户
                _rt_customer = CustomerInfo()
                # 保存最关键的手机信息
                _rt_customer.mobile = order.receiver_mobile

                # 尝试获取平台信息。如果拿到平台信息，则进行对应的平台ID的赋值
                # 更新平台ID信息
                _rt_customer = self.transplatformnick(_rt_customer, order)

                _rt_customer.name = order.receiver_name
                _rt_customer.address = order.receiver_address

                # 对区域信息进行处理，前置处理一下，因为区域在订单中是一个字段保存着省市区
                _pre_area = order.receiver_area.split(' ')

                # 省市区都有的情况
                if len(_pre_area) == 3:
                    _rt_customer.province = _pre_area[0]
                    _rt_customer.city = _pre_area[1]
                    _rt_customer.district = _pre_area[2]

                # 没有区县的情况
                elif len(_pre_area) == 2:
                    _rt_customer.province = _pre_area[0]
                    _rt_customer.city = _pre_area[1]

                # 其他异常情况，就舍弃这几个字段的保存。
                else:
                    report_dic["error_area"] += 1


                try:
                    _rt_customer.save()
                    report_dic["create_cus_success"] += 1
                except Exception as e:
                    report_dic['create_cus_fail'] += 1
                    continue

                intermediate_report_dic = self.updatecustomer(order)

                for k, v in intermediate_report_dic.items():
                    report_dic[k] += v

        return report_dic

    def updatecustomer(self, order):
        report_dic = {"create_cus_success": 0, "create_cus_fail": 0, "order_success": 0, "order_fail": 0,
                      "error_area": 0, "discard": 0, "update_cus_success": 0, "update_cus_fail": 0}
        # 对客户信息进行更新。传入查询到的客户对象_rt_customer，传入对应的客户更新信息customer。
        # 如果订单有收款金额。
        intermediate_customer = CustomerInfo.objects.filter(mobile=order.receiver_mobile)[0]

        if order.allocated_total_fee > 0 and order.status != "已取消":

            intermediate_customer.total_fee += order.allocated_total_fee

            if OrderInfo.objects.filter(sub_original_order_id=order.sub_original_order_id, tocustomer_status=str(1)):
                pass
            else:
                intermediate_customer.total_times += 1
            intermediate_customer.last_time = order.pay_time

            # 设置订单客户信息生成状态。
            order.tocustomer_status = 1
            # 更新对应的客户信息，保存对应的订单信息
            report_dic = self.savecustomer(intermediate_customer, order)
            return report_dic

        else:
            if order.status != "已取消":
                # 如果没有收款金额
                # 判断如果是保修单
                if order.order_type == '保修完成':
                    intermediate_customer.maintenance_times += 1
                    order.tocustomer_status = 1
                    report_dic = self.savecustomer(intermediate_customer, order)
                    return report_dic

                # 判断如果是售后换货
                elif order.order_type == '售后换货':
                    intermediate_customer.customers_service_times += 1
                    order.tocustomer_status = 1
                    report_dic = self.savecustomer(intermediate_customer, order)
                    return report_dic

                # 判断如果是手工新建的配件，或者整机，归集到售后或者赠品
                elif order.order_type in ['线下零售', '网店销售']:
                    if order.order_source == '手工建单':
                        intermediate_customer.customers_service_times += 1
                        order.tocustomer_status = 1
                        report_dic = self.savecustomer(intermediate_customer, order)
                        return report_dic

                    # 其他类型统一归集到赠品
                    else:
                        intermediate_customer.gift_times += 1
                        order.tocustomer_status = 1
                        report_dic = self.savecustomer(intermediate_customer, order)
                        return report_dic

                else:
                    order.tocustomer_status = 2
                    report_dic = self.savecustomer(intermediate_customer, order)
                    report_dic["discard"] += 1
                    return report_dic
            else:
                intermediate_customer.order_failure_times += 1
                order.tocustomer_status = 3
                report_dic = self.savecustomer(intermediate_customer, order)
                return report_dic

    def transplatformnick(self, _rt_customer, customer):

        # 针对不同的平台，进行不同的终端软件ID的保存
        platform_dic = {"淘宝": "wangwang", "京东FBP": "jdfbp_id", "京东自营": "jdzy_id", "官方商城": "gfsc_id",
                        "微信小程序": "wxxcx_id", "拼多多": "pdd_id"}

        # 尝试获取平台信息。如果拿到平台信息，则进行对应的平台ID的赋值
        _rt_platform = platform_dic.get(customer.platform, None)
        if _rt_platform is not None:
            setattr(_rt_customer, _rt_platform, customer.buyer_nick)
        return _rt_customer

    def savecustomer(self, _rt_customer, customer):

        report_dic = {"create_cus_success": 0, "create_cus_fail": 0, "order_success": 0, "order_fail": 0,
                      "error_area": 0, "discard": 0, "update_cus_success": 0, "update_cus_fail": 0}

        # 保存客户信息，确认客户信息已经完成，这个应该有一个逻辑关系，先保存客户信息，成功了，在保存订单信息。后面再改
        try:
            _rt_customer.save()
            report_dic["update_cus_success"] += 1

            # 保存订单状态信息。确认订单已经完成
            try:
                customer.save()
                report_dic["order_success"] += 1
            except Exception as e:
                report_dic["order_fail"] += 1

        except Exception as e:
            report_dic["update_cus_fail"] += 1
            print(e)

        return report_dic


class OrderToTendency(View):
    def get(self, request: object) -> object:
        pass

    def post(self, request):
        pass




























