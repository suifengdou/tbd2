# -*- coding: utf-8 -*-
# @Time    : 2020/11/12 16:36
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import math, re, operator
import datetime
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse
from django.db.models import Sum, Avg, Min, Max, F
from django.db import models

from django.contrib.admin.utils import get_deleted_objects

import pandas as pd
import numpy as np
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side


from .models import WorkOrderDealerPart, SubmitWODP, CheckWODP
from apps.base.goods.models import GoodsInfo
from apps.assistants.giftintalk.models import GiftOrderInfo
from apps.base.shop.models import ShopInfo
from apps.utils.geography.models import CityInfo

ACTION_CHECKBOX_NAME = '_selected_action'


class RejectSelectedAction(BaseActionView):

    action_name = "reject_selected"
    description = '驳回选中的单据'

    delete_confirmation_template = None
    delete_selected_confirmation_template = None

    delete_models_batch = False

    model_perm = 'change'
    icon = 'fa fa-times'

    @filter_hook
    def reject_models(self, queryset):
        n = queryset.count()
        if n:
            for obj in queryset:

                if isinstance(obj, WorkOrderDealerPart):
                    obj.order_status -= 1
                    obj.process_tag = 5
                    if obj.order_status == 0:
                        self.message_user("%s 取消成功" % obj.order_id, "success")
                    obj.save()
            self.message_user("成功驳回 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None

    @filter_hook
    def do_action(self, queryset):
        # Check that the user has delete permission for the actual model
        if not self.has_change_permission():
            raise PermissionDenied

        using = router.db_for_write(self.model)

        # Populate deletable_objects, a data structure of all related objects that
        # will also be deleted.
        deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
            queryset, self.opts, self.user, self.admin_site, using)

        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if self.request.POST.get('post'):
            if not self.has_change_permission():
                raise PermissionDenied
            self.reject_models(queryset)
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_text(self.opts.verbose_name)
        else:
            objects_name = force_text(self.opts.verbose_name_plural)
        perms_needed = []
        if perms_needed or protected:
            title = "Cannot reject %(name)s" % {"name": objects_name}
        else:
            title = "Are you sure?"

        context = self.get_context()
        context.update({
            "title": title,
            "objects_name": objects_name,
            "deletable_objects": [deletable_objects],
            'queryset': queryset,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": self.opts,
            "app_label": self.app_label,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        })

        # Display the confirmation page
        return TemplateResponse(self.request, self.delete_selected_confirmation_template or
                                self.get_template_list('views/model_reject_selected_confirm.html'), context)


# 提交赠品信息到订单
class SubmitWODPAction(BaseActionView):
    action_name = "submit_wodp"
    description = "提交选中的配件订单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            for obj in queryset:
                _q_repeat_order = WorkOrderDealerPart.objects.filter(order_id=obj.order_id,
                                                                     order_status__in=[2, 3])
                if _q_repeat_order.exists():
                    if obj.process_tag != 6:
                        self.message_user("%s一个订单号不可重复提交" % obj.order_id, "error")
                        n -= 1
                        obj.mistake_tag = 1
                        obj.save()
                        continue
                _q_repeat_order_smart = WorkOrderDealerPart.objects.filter(sent_smartphone=obj.sent_smartphone,
                                                                           order_status__in=[2, 3])
                if _q_repeat_order_smart.exists():
                    if obj.process_tag != 6:
                        self.message_user("%s电话重复" % obj.order_id, "error")
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                if '整机' in obj.parts_info:
                    self.message_user("%s货品名称包含整机不是配件" % obj.order_id, "error")
                    n -= 1
                    obj.mistake_tag = 3
                    obj.save()
                    continue

                goods_group = self.goods_split(obj.parts_info)
                error_tag = 0
                for goods_info in goods_group:
                    # 对货品进行处理
                    goods_list = str(goods_info).split("*")
                    if len(goods_list) == 2:
                        goods_info = GoodsInfo.objects.filter(goods_name=goods_list[0])
                        if not goods_info.exists():
                            error_tag = 1
                            break
                if error_tag:
                    self.message_user("%s货品名称错误，修正后再次重新提交，如果名称无误，请联系管理员" % obj.order_id, "error")
                    n -= 1
                    obj.mistake_tag = 4
                    obj.save()
                    continue

                if obj.shop.shop_name != '旗舰店供应商':
                    self.message_user("%s店铺错误" % obj.order_id, "error")
                    n -= 1
                    obj.mistake_tag = 5
                    obj.save()
                    continue

                if re.match(r'^1', obj.sent_smartphone):
                    if len(obj.sent_smartphone) != 11:
                        self.message_user("%s手机出错" % obj.order_id, "error")
                        n -= 1
                        obj.mistake_tag = 6
                        obj.save()
                        continue
                if '集运' in str(obj.sent_address):
                    self.message_user("%s地址是集运仓" % obj.order_id, "error")
                    n -= 1
                    obj.mistake_tag = 7
                    obj.save()
                    continue
                if not ((obj.sent_consignee and obj.sent_address) and obj.sent_smartphone):
                    self.message_user("%s收货人电话地址不全" % obj.order_id, "error")
                    n -= 1
                    obj.mistake_tag = 8
                    obj.save()
                    continue
                special_city = ['仙桃市', '天门市', '神农架林区', '潜江市', '济源市', '五家渠市', '图木舒克市', '铁门关市', '石河子市', '阿拉尔市',
                                '嘉峪关市', '五指山市', '文昌市', '万宁市', '屯昌县', '三亚市', '三沙市', '琼中黎族苗族自治县', '琼海市',
                                '陵水黎族自治县', '临高县', '乐东黎族自治县', '东方市', '定安县', '儋州市', '澄迈县', '昌江黎族自治县', '保亭黎族苗族自治县',
                                '白沙黎族自治县', '中山市', '东莞市']
                if obj.sent_city.city not in special_city:
                    if not obj.sent_district:
                        self.message_user("%s此地址三级区县必填" % obj.order_id, "error")
                        n -= 1
                        obj.mistake_tag = 12
                        obj.save()
                        continue
                if obj.order_category in [1, 2]:
                    if not all([obj.m_sn, obj.broken_part, obj.description]):
                        self.message_user("%s售后配件需要补全sn、部件和描述" % obj.order_id, "error")
                        n -= 1
                        obj.mistake_tag = 13
                        obj.save()
                        continue
                self.log('change', '提交经销商配件订单', obj)
                obj.order_status = 2
                obj.submit_time = datetime.datetime.now()
                obj.mistake_tag = 0
                obj.process_tag = 0
                obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None

    def goods_split(self, goods):

        if "+" in goods:
            goods_group = goods.split("+")
        else:
            goods_group = [goods]

        for i in range(len(goods_group)):
            goods_group[i] = str(goods_group[i]).replace("\xa0", " ")
        return goods_group


class CheckWODPAction(BaseActionView):
    action_name = "submit_wodp"
    description = "提交选中的配件订单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            for obj in queryset:

                _q_repeat_order_smart = WorkOrderDealerPart.objects.filter(sent_smartphone=obj.sent_smartphone,
                                                                           order_status=3)
                if _q_repeat_order_smart.exists():
                    if obj.process_tag != 6:
                        self.message_user("%s电话重复" % obj.order_id, "error")
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue

                goods_group = self.goods_split(obj.parts_info)
                error_tag = 0
                for goods_info in goods_group:
                    # 对货品进行处理
                    gift_order = GiftOrderInfo()

                    goods_list = str(goods_info).split("*")
                    if len(goods_list) == 2:
                        gift_order.quantity = goods_list[1]
                        goods_info = GoodsInfo.objects.filter(goods_name=goods_list[0])
                        if goods_info.exists():
                            gift_order.goods_name = goods_info[0].goods_name
                            gift_order.goods_id = goods_info[0].goods_id
                        else:
                            self.message_user("%s货品名称错误，修正后再次重新提交，如果名称无误，请联系管理员" % obj.order_id, "error")
                            n -= 1
                            obj.mistakes = 4
                            obj.save()
                            continue
                    order_id = str(obj.order_id).replace("订单号", "").replace(" ", "").replace("：", "")
                    gift_order.order_id = order_id

                    gift_order.nickname = str(obj.nickname).replace("客户ID", "").replace(" ", "").replace("：", "").replace("顾客ID", "")
                    # 用户名和货品确认递交是否是唯一
                    _gift_checked = GiftOrderInfo.objects.filter(goods_id=gift_order.goods_id,
                                                                 mobile=obj.sent_smartphone)
                    if _gift_checked.exists():
                        delta_date = (obj.create_time - _gift_checked[0].create_time).days
                        if obj.process_tag != 6:
                            if int(delta_date) > 14:
                                self.message_user("%s14天内重复" % obj.order_id, "error")
                                n -= 1
                                obj.mistakes = 5
                                obj.save()
                                continue
                            else:
                                self.message_user("%s14天外重复" % obj.order_id, "error")
                                n -= 1
                                obj.mistakes = 4
                                obj.save()
                                continue
                    special_city = ['仙桃市', '天门市', '神农架林区', '潜江市', '济源市', '五家渠市', '图木舒克市', '铁门关市', '石河子市', '阿拉尔市',
                                    '嘉峪关市', '五指山市', '文昌市', '万宁市', '屯昌县', '三亚市', '三沙市', '琼中黎族苗族自治县', '琼海市',
                                    '陵水黎族自治县', '临高县', '乐东黎族自治县', '东方市', '定安县', '儋州市', '澄迈县', '昌江黎族自治县', '保亭黎族苗族自治县',
                                    '白沙黎族自治县', '中山市', '东莞市']
                    if obj.sent_city.city in special_city:
                        gift_order.province = obj.sent_city.province.province
                        gift_order.city = obj.sent_city.city
                    else:
                        gift_order.province = obj.sent_city.province.province
                        gift_order.city = obj.sent_city.city
                        gift_order.district = obj.sent_district
                    gift_order.address = obj.sent_address
                    gift_order.receiver = obj.sent_consignee
                    gift_order.creator = self.request.user.username
                    gift_order.shop = obj.shop.shop_name
                    if gift_order.shop != '旗舰店供应商':
                        self.message_user("%s店铺错误" % obj.order_id, "error")
                        n -= 1
                        obj.mistakes = 5
                        obj.save()
                        continue

                    gift_order.order_category = obj.order_category
                    gift_order.shop = obj.shop.shop_name
                    gift_order.buyer_remark = "旗舰店供应商 %s客服%s赠送客户%s赠品%sx%s" % \
                                              (str(obj.update_time)[:11], obj.creator,
                                               gift_order.nickname, gift_order.goods_name, gift_order.quantity)
                    gift_order.cs_memoranda = "%sx%s" % (gift_order.goods_name, gift_order.quantity)
                    gift_order.submit_user = self.request.user.username
                    gift_order.mobile = obj.sent_smartphone

                    try:
                        gift_order.save()
                    except Exception as e:
                        self.message_user("%s出错:%s" % (obj.order_id, e), "error")
                        error_tag = 1
                        continue
                if error_tag:
                    n -= 1
                    obj.mistake_tag = 11
                    obj.save()
                    continue
                self.log('change', '审核经销商配件单', obj)
                obj.handle_time = datetime.datetime.now()
                obj.handler = self.request.user.username
                start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                d_value = end_time - start_time
                days_seconds = d_value.days * 3600
                total_seconds = days_seconds + d_value.seconds
                obj.handle_interval = math.floor(total_seconds / 60)
                obj.order_status = 3
                obj.mistake_tag = 0
                obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None

    def goods_split(self, goods):

        if "+" in goods:
            goods_group = goods.split("+")
        else:
            goods_group = [goods]

        for i in range(len(goods_group)):
            goods_group[i] = str(goods_group[i]).replace("\xa0", " ")
        return goods_group


# 提交赠品信息到订单
class SetWODPSAction(BaseActionView):
    action_name = "set_wodp_special"
    description = "设置选中为特殊订单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            queryset.update(process_tag=6)
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


class SetWODPCAction(BaseActionView):
    action_name = "set_wodp_clear"
    description = "清除选中订单标记"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            queryset.update(process_tag=0)
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


class SubmitWODPAdmin(object):
    list_display = ['shop', 'order_id', 'process_tag', 'mistake_tag', 'feedback', 'nickname', 'sent_consignee',
                    'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'parts_info',
                    'message', 'sign_company', 'sign_department',
                    'order_category', 'creator', 'create_time', 'update_time', 'order_status']
    actions = [SetWODPSAction, SetWODPCAction, SubmitWODPAction, RejectSelectedAction]

    search_fields = ['sent_smartphone', 'order_id']
    list_filter = ['order_id', 'sent_smartphone', 'sent_consignee', 'process_tag', 'creator', 'mistake_tag', 'parts_info', 'create_time']

    list_editable = ['sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'parts_info',
                     'sent_address', 'message', ]

    readonly_fields = []

    form_layout = [
        Fieldset('基本信息',
                 'shop',
                 Row('order_id', 'nickname'),
                 'parts_info', 'order_category', ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company',
                 'sign_department', 'submit_time', 'handle_time', 'handler', 'handle_interval', 'feedback',
                 **{"style": "display:None"}),
    ]
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {
        '源订单号': 'order_id',
        '店铺': 'shop',
        '客户网名': 'nickname',
        '收件人姓名': 'sent_consignee',
        '收件人手机': 'sent_smartphone',
        '收件城市': 'sent_city',
        '收件区县': 'sent_district',
        '收件地址': 'sent_address',
        '配件信息': 'parts_info',
        '备注': 'message'
    }
    import_data = True

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('导入成功数据%s条' % int(result['successful']), 'success')
            if result['false'] > 0 or result['error']:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (int(result['false']), result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('包含更新重复数据%s条' % int(result['repeated']), 'error')
        return super(SubmitWODPAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0)

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = WorkOrderDealerPart.verify_mandatory(columns_key)
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
                _ret_verify_field = WorkOrderDealerPart.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field
                # 验证通过进行重新处理。
                columns_key_ori = piece.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                piece.rename(columns=ret_columns_key, inplace=True)
                _ret_list = piece.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(request, _ret_list)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
            return report_dic

        else:
            report_dic["error"].append('只支持excel和csv文件格式！')
            return report_dic

    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}

        # 开始导入数据
        for row in resource:
            error_tag = 0
            order = WorkOrderDealerPart()  # 创建表格每一行为一个对象
            required_fields = ['order_id', 'shop', 'nickname', 'sent_consignee', 'sent_smartphone', 'sent_city',
                               'sent_address', 'parts_info', 'message']
            for required_word in required_fields:
                if not row[required_word]:
                    report_dic["discard"] += 1
                    report_dic['error'].append("%s 必填字段：%s 为空" % (str(row['order_id']), str(row[required_word])))
                    error_tag = 1
                    break
            if error_tag:
                continue
            order_id = str(row["order_id"])

            parts_info = str(row["parts_info"])
            shop = str(row["shop"])
            if shop != "旗舰店供应商":
                report_dic["discard"] += 1
                report_dic['error'].append("%s 店铺错误" % order_id)
                continue
            _shop_ob = ShopInfo.objects.filter(shop_name=shop)
            if _shop_ob.exists():
                order.shop = _shop_ob[0]
            else:
                report_dic["discard"] += 1
                report_dic['error'].append("%s 无法匹配到店铺" % order_id)
                continue
            city = row["sent_city"]
            _city_ob = CityInfo.objects.filter(city=city)
            if _city_ob.exists():
                order.sent_city = _city_ob[0]
            else:
                report_dic["discard"] += 1
                report_dic['error'].append("%s 二级城市：%s 错误" % (order_id, city))
                continue

            if len(parts_info) > 299:
                row["information"] = parts_info[:298]
            # 如果服务单号已经存在，丢弃订单，计数为重复订单
            if WorkOrderDealerPart.objects.filter(order_id=order_id, order_status__in=[1, 2, 3]).exists():
                report_dic["repeated"] += 1
                continue
            else:
                order_fields = ['order_id', 'nickname', 'sent_consignee', 'sent_smartphone',
                                'sent_district', 'sent_address', 'parts_info', 'message']
                for key in order_fields:

                    # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
                    if hasattr(order, key):
                        if row[key] in ['nan', 'NaT']:
                            pass
                        else:
                            setattr(order, key, row[key])  # 更新对象属性为字典对应键值
                try:
                    order.creator = request.user.username
                    order.sign_company = request.user.company
                    order.sign_department = request.user.department
                    order.save()
                    report_dic["successful"] += 1
                # 保存出错，直接错误条数计数加一。
                except Exception as e:
                    report_dic["false"] += 1
                    report_dic["error"].append(e)
        return report_dic

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username

        if not obj.sign_company:
            if request.user.company:
                obj.sign_company = request.user.company
        if not obj.sign_department:
            obj.sign_department = request.user.department
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(SubmitWODPAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0, creator=self.request.user.username)
        return queryset


class CheckWODPAdmin(object):
    list_display = ['shop', 'order_id', 'process_tag', 'mistake_tag', 'feedback', 'sent_consignee', 'sent_smartphone', 'sent_city',
                    'sent_district', 'sent_address', 'parts_info', 'message', 'sign_company', 'sign_department',
                    'order_category', 'creator', 'create_time', 'update_time', 'order_status']
    actions = [SetWODPSAction, SetWODPCAction, CheckWODPAction, RejectSelectedAction]

    search_fields = ['sent_smartphone', 'order_id']
    list_filter = ['order_id', 'sent_consignee', 'sent_smartphone', 'process_tag', 'creator', 'mistake_tag', 'parts_info', 'create_time']

    list_editable = ['feedback']

    readonly_fields = ['shop', 'order_id', 'process_tag', 'mistake_tag', 'sent_consignee', 'sent_smartphone',
                       'sent_city', 'sent_district', 'sent_address', 'parts_info', 'message', 'sign_company',
                       'sign_department', 'order_category', 'creator', 'create_time', 'update_time', 'order_status',
                       'nickname', 'submit_time', 'handler', 'handle_time', 'handle_interval', 'is_delete']

    form_layout = [
        Fieldset('基本信息',
                 'feedback',
                 'shop', 'parts_info', 'order_category', ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company',
                 'sign_department', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(CheckWODPAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0)
        return queryset


class WorkOrderDealerPartAdmin(object):
    list_display = ['shop', 'order_id', 'process_tag', 'mistake_tag', 'feedback', 'sent_consignee', 'sent_smartphone',
                    'sent_city', 'sent_district', 'sent_address', 'parts_info', 'message', 'sign_company',
                    'sign_department', 'order_category', 'creator', 'create_time', 'update_time', 'order_status']

    search_fields = ['sent_smartphone', 'order_id']
    list_filter = ['order_id', 'sent_consignee', 'process_tag', 'creator', 'mistake_tag', 'parts_info', 'sent_smartphone',
                   'create_time']
    readonly_fields = ['shop', 'order_id', 'process_tag', 'mistake_tag', 'sent_consignee', 'sent_smartphone',
                       'sent_city', 'sent_district', 'sent_address', 'parts_info', 'message', 'sign_company',
                       'sign_department', 'order_category', 'creator', 'create_time', 'update_time', 'order_status',
                       'nickname', 'submit_time', 'handler', 'handle_time', 'handle_interval', 'feedback', 'is_delete']

    def queryset(self):
        queryset = super(WorkOrderDealerPartAdmin, self).queryset()
        if self.request.user.category:
            queryset = queryset.filter(is_delete=0)
        else:
            queryset = queryset.filter(is_delete=0, creator=self.request.user.username)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(SubmitWODP, SubmitWODPAdmin)
xadmin.site.register(CheckWODP, CheckWODPAdmin)
xadmin.site.register(WorkOrderDealerPart, WorkOrderDealerPartAdmin)


