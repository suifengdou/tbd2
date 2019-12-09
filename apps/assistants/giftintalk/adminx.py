# -*- coding: utf-8 -*-
# @Time    : 2019/10/18 20:29
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm
import math, re
import datetime
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse

from django.contrib.admin.utils import get_deleted_objects

from django.core.files.uploadedfile import InMemoryUploadedFile

import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset

from .models import GiftInTalkPendding, GiftInTalkInfo, GiftOrderPendding, GiftOrderInfo, GiftImportInfo, GiftImportPendding, GiftInTalkRepeat
from apps.base.goods.models import GoodsInfo
from apps.utils.geography.models import CityInfo, DistrictInfo

ACTION_CHECKBOX_NAME = '_selected_action'


# 驳回审核
class RejectSelectedAction(BaseActionView):
    action_name = "reject_selected"
    description = '驳回选中的订单'

    delete_confirmation_template = None
    delete_selected_confirmation_template = None

    delete_models_batch = False

    model_perm = 'change'
    icon = 'fa fa-times'

    @filter_hook
    def delete_models(self, queryset):
        n = queryset.count()
        if n:
            queryset.update(order_status=0)
            self.message_user("成功驳回 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None

    @filter_hook
    def do_action(self, queryset):
        # Check that the user has delete permission for the actual model
        if not self.has_delete_permission():
            raise PermissionDenied

        using = router.db_for_write(self.model)

        # Populate deletable_objects, a data structure of all related objects that
        # will also be deleted.
        deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
            queryset, self.opts, self.user, self.admin_site, using)

        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if self.request.POST.get('post'):
            if perms_needed:
                raise PermissionDenied
            self.delete_models(queryset)
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_text(self.opts.verbose_name)
        else:
            objects_name = force_text(self.opts.verbose_name_plural)

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
class SubmitGiftAction(BaseActionView):
    action_name = "submit_r_wo"
    description = "提交选中的赠品订单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if self.request.user.username in ['王贺宽', '张国帅']:
            PLATFORM = {2: '京东', 1: '淘系'}
            if n:
                for obj in queryset:
                    goods_group = self.goods_split(obj.goods)
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
                                obj.mistakes = 0
                                obj.save()
                                continue
                        order_id = str(obj.order_id).replace("订单号", "").replace(" ", "").replace("：", "")
                        gift_order.order_id = order_id

                        gift_order.nickname = str(obj.nickname).replace("客户ID", "").replace(" ", "").replace("：", "").replace("顾客ID", "")
                        if len(gift_order.nickname) == 0:
                            self.message_user("%s客户网名错误" % obj.order_id, "error")
                            n -= 1
                            obj.mistakes = 5
                            obj.save()
                            continue

                        # 用订单号和货品确认递交是否是唯一
                        _gift_checked = GiftOrderInfo.objects.filter(goods_id=gift_order.goods_id, nickname=gift_order.nickname)
                        if _gift_checked.exists():
                            delta_date = (obj.create_time - _gift_checked[0].create_time).days
                            if int(delta_date) > 14:
                                n -= 1
                                obj.mistakes = 2
                                obj.save()
                                continue
                            else:
                                n -= 1
                                obj.mistakes = 1
                                obj.save()
                                continue

                        cs_info = str(obj.cs_information).replace("收货信息", "").replace("：", "").split(" ")
                        if len(cs_info) == 3:
                            gift_order.receiver = cs_info[0]
                            gift_order.mobile = cs_info[1]
                            gift_order.address = cs_info[2]
                        elif len(cs_info) > 3:
                            gift_order.receiver = cs_info[0]
                            gift_order.mobile = cs_info[1]
                            address = str(cs_info[2])
                            for i in range(len(cs_info)):
                                if i > 2:
                                    address = address + str(cs_info[i])
                            gift_order.address = address
                        else:
                            self.message_user("%s收货信息错误，修正后再次重新提交，请严格按照要求提交" % obj.order_id, "error")
                            n -= 1
                            obj.mistakes = 3
                            obj.save()
                            continue
                        special_city = ['仙桃市', '天门市', '神农架林区', '潜江市', '济源市', '五家渠市', '图木舒克市', '铁门关市', '石河子市', '阿拉尔市',
                                        '嘉峪关市', '五指山市', '文昌市', '万宁市', '屯昌县', '三亚市', '三沙市', '琼中黎族苗族自治县', '琼海市',
                                        '陵水黎族自治县', '临高县', '乐东黎族自治县', '东方市', '定安县', '儋州市', '澄迈县', '昌江黎族自治县', '保亭黎族苗族自治县',
                                        '白沙黎族自治县', '中山市', '东莞市']
                        # 京东地址处理逻辑
                        if obj.platform == 2:
                            _province_key = gift_order.address[:2]
                            if _province_key in ['内蒙', '黑龙']:
                                _province_key = gift_order.address[:3]

                            if _province_key in ['北京', '天津', '上海', '重庆']:
                                _city_key = _province_key + "市"
                            elif "州" in gift_order.address:
                                _city_key = gift_order.address[len(_province_key):len(_province_key) + 2]
                            else:
                                _city_key = gift_order.address[len(_province_key):len(_province_key) + 3]

                            _rt_city = CityInfo.objects.filter(city__contains=_city_key)
                            if _rt_city.exists():
                                gift_order.province = _rt_city[0].province.province
                                gift_order.city = _rt_city[0].city

                                if _province_key in ['北京', '天津', '上海', '重庆']:
                                    _district_key = gift_order.address[len(_province_key):len(_province_key) + 2]
                                    _rt_districts = DistrictInfo.objects.filter(city=_rt_city[0],
                                                                                district__contains=_district_key)
                                    if _rt_districts.exists():
                                        gift_order.district = _rt_districts[0].district
                                    else:
                                        gift_order.district = '其他区'

                                elif "州" in gift_order.city:
                                    tag_position = gift_order.address.index("州", 3)
                                    _district_key = gift_order.address[tag_position + 1:tag_position + 2]
                                    _rt_districts = DistrictInfo.objects.filter(city=_rt_city[0],
                                                                                district__contains=_district_key)
                                    if _rt_districts.exists():
                                        gift_order.district = _rt_districts[0].district
                                    else:
                                        tag_position = gift_order.address.index("市", 4)
                                        _district_key = gift_order.address[tag_position + 1:tag_position + 2]
                                        _rt_districts = DistrictInfo.objects.filter(city=_rt_city[0],
                                                                                    district__contains=_district_key)
                                        if _rt_districts.exists():
                                            gift_order.district = _rt_districts[0].district
                                        else:
                                            gift_order.district = '其他区'
                                elif gift_order.city not in special_city:
                                    _district_key = gift_order.address[
                                                    len(_province_key) + len(_rt_city[0].city):len(_province_key) + len(
                                                        _rt_city[0].city) + 2]
                                    _rt_districts = DistrictInfo.objects.filter(city=_rt_city[0],
                                                                                district__contains=_district_key)

                                    if _rt_districts.exists():
                                        gift_order.district = _rt_districts[0].district
                                    else:
                                        gift_order.district = '其他区'
                            else:
                                self.message_user("%s地址中二级城市出错，请修正后提交" % obj.order_id, "error")
                                n -= 1
                                obj.mistakes = 4
                                obj.save()
                                continue
                        # 淘宝地址处理逻辑
                        elif obj.platform == 1:
                            keywords = gift_order.address.split('，')
                            if len(keywords) > 2:
                                _city_key = keywords[1]
                                _rt_city = CityInfo.objects.filter(city__contains=_city_key)
                                if _rt_city.exists():
                                    gift_order.province = _rt_city[0].province.province
                                    gift_order.city = _rt_city[0].city
                                    if _city_key not in special_city:
                                        _district_key = keywords[2][:2]
                                        _rt_districts = DistrictInfo.objects.filter(city=_rt_city[0], district__contains=_district_key)
                                        if _rt_districts.exists():
                                            gift_order.district = _rt_districts[0].district
                                        else:
                                            gift_order.district = '其他区'
                                else:
                                    self.message_user("%s地址不是淘宝默认地址，请修正成淘宝默认格式后提交" % obj.order_id, "error")
                                    n -= 1
                                    obj.mistakes = 4
                                    obj.save()
                                    continue
                        gift_order.order_category = obj.order_category
                        gift_order.shop = obj.platform
                        gift_order.buyer_remark = "%s %s客服%s赠送客户%s赠品%sx%s" % (PLATFORM[obj.platform], str(obj.update_time)[:11], obj.servicer, gift_order.nickname, gift_order.goods_name,gift_order.quantity)
                        gift_order.cs_memoranda = "%sx%s" % (gift_order.goods_name, gift_order.quantity)
                        gift_order.submit_user = self.request.user.username
                        gift_order.creator = self.request.user.username
                        try:
                            gift_order.save()
                        except Exception as e:
                            self.message_user("%s出错:%s" % (obj.order_id, e), "error")
                            n -= 1
                            obj.mistakes = 6
                            obj.save()
                            continue

                        self.log('change', '', obj)
                        obj.order_status = 2
                        obj.save()

                self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        else:
            self.message_user("%s 没有递交订单的权限，只有特定的账号才能操作递交订单。" % self.request.user.username, "error")
            return None

        return None

    def goods_split(self, goods):

        if "+" in goods:
            goods_group = goods.split("+")
        else:
            goods_group = [goods]

        for i in range(len(goods_group)):
            goods_group[i] = str(goods_group[i]).replace("\xa0", " ")
        return goods_group


# 礼品订单提交
class SubmitAction(BaseActionView):
    action_name = "submit_wo"
    description = "提交选中的订单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(status=2)
            else:
                for obj in queryset:
                    import_order = GiftImportInfo()
                    repeat_cs = GiftImportInfo.objects.filter(address=obj.address, mobile=obj.mobile, order_status=1)
                    if repeat_cs.exists():
                        repeat_cs_order = repeat_cs[0]
                        add_goods = "%sx%s" % (obj.goods_name, obj.quantity)
                        repeat_cs_order.buyer_remark = repeat_cs_order.buyer_remark + "+" + add_goods
                        repeat_cs_order.cs_memoranda = repeat_cs_order.cs_memoranda + "+" + add_goods
                        # 针对那种强迫症，玩命点递交的人，需要进行去重。
                        goods_list = repeat_cs_order.cs_memoranda
                        if "+" in goods_list:
                            goods_list = str(goods_list).split("+")
                            goods_list = [i[:-2] for i in goods_list]
                        repeat_tag = True
                        for i in goods_list:
                            if goods_list.count(i) > 1:
                                self.message_user("%s不要重复递交，不要重复递交！点一次等着就好！！！" % obj.nickname, "error")
                                obj.order_status = 2
                                obj.save()
                                repeat_tag = False
                                break
                        if repeat_tag:
                            repeat_cs_order.save()
                    else:
                        _prefix = "GT"
                        serial_number = str(datetime.datetime.now())
                        serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".",
                                                                                                                 "")
                        import_order.erp_order_id = _prefix + str(serial_number)[0:17] + "A"
                        import_order.shop = obj.shop
                        import_order.nickname = obj.nickname
                        import_order.receiver = obj.receiver
                        import_order.address = obj.address
                        import_order.mobile = obj.mobile
                        import_order.goods_id = obj.goods_id
                        import_order.goods_name = obj.goods_name
                        import_order.quantity = obj.quantity
                        import_order.province = obj.province
                        import_order.city = obj.city
                        import_order.district = obj.district
                        import_order.order_id = obj.order_id
                        import_order.buyer_remark = obj.buyer_remark
                        import_order.cs_memoranda = obj.cs_memoranda
                        import_order.creator = self.request.user.username
                        try:
                            import_order.save()
                        except Exception as e:
                            self.message_user("%s递交出现错误:%s" % (obj.order_id, e), "info")

                    self.log('change', '', obj)
                    obj.submit_user = self.request.user.username
                    obj.order_status = 2
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class SubmitImportAction(BaseActionView):
    action_name = "submit_wo"
    description = "提交选中的订单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(status=2)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.submit_user = self.request.user.username
                    obj.order_status = 2
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 对话信息导入和处理
class GiftInTalkPenddingAdmin(object):
    list_display = ['platform',  'order_status', 'mistakes', 'cs_information', 'goods', 'nickname', 'order_category', 'order_id', 'servicer', 'creator']
    list_filter = ['mistakes', 'create_time', 'creator', 'order_category']
    list_editable = ['goods', 'nickname', 'order_id', 'cs_information']
    search_fields = ['nickname', 'order_id']

    ALLOWED_EXTENSIONS = ['log', 'txt']
    actions = [SubmitGiftAction, RejectSelectedAction]
    import_data = True

    def post(self, request, *args, **kwargs):
        result = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        _rt_talk_title = ['servicer', 'goods', 'nickname', 'order_id', 'cs_information']
        _rt_talk_title_new = ['order_category', 'servicer', 'goods', 'nickname', 'order_id', 'cs_information']
        file = request.FILES.get('file', None)
        if request.user.platform:
            if file:
                file.open()
                while True:
                    s = file.readline()
                    if s:
                        if request.user.platform == 2:
                            s = s.decode("utf-8")
                        elif request.user.platform == 1:
                            s = s.decode("GBK")

                        if "·客服" in s:
                            _rt_talk_data = re.findall(r"{(.*?)}", s)
                            _rt_talk = GiftInTalkInfo()
                            _rt_talk.creator = request.user.username
                            if len(_rt_talk_data) == 5:
                                _rt_talk.platform = 2
                                _rt_talk_dic = dict(zip(_rt_talk_title, _rt_talk_data))
                                for k, v in _rt_talk_dic.items():
                                    if hasattr(_rt_talk, k):
                                        setattr(_rt_talk, k, v)
                                try:
                                    _rt_talk.save()
                                    result["successful"] += 1
                                except Exception as e:
                                    result["false"] += 1
                                    result["error"].append(e)
                            elif len(_rt_talk_data) == 6:
                                _rt_talk.platform = 2
                                _rt_talk_dic = dict(zip(_rt_talk_title_new, _rt_talk_data))
                                for k, v in _rt_talk_dic.items():
                                    if hasattr(_rt_talk, k):
                                        setattr(_rt_talk, k, v)
                                try:
                                    _rt_talk.save()
                                    result["successful"] += 1
                                except Exception as e:
                                    result["false"] += 1
                                    result["error"].append(e)
                            elif len(_rt_talk_data) == 4:
                                _rt_talk.platform = 1
                                _rt_talk.order_category = _rt_talk_data[0]
                                _rt_talk.servicer = _rt_talk_data[1]
                                _rt_talk.goods = _rt_talk_data[2]
                                cs_informations = _rt_talk_data[3].split('\r')
                                if len(cs_informations) in [5, 6]:
                                    _rt_talk.nickname = cs_informations[1].replace('收货信息买家ID\u3000：', '客户ID')
                                    consignee = cs_informations[2].replace('收货人\u3000：', '收货信息')
                                    address = cs_informations[3].replace('收货地址：', '')
                                    mobile = cs_informations[5].replace('电\u3000\u3000话：', '')
                                    information = [consignee, mobile, address]
                                    _rt_talk.cs_information = ' '.join(information)
                                    try:
                                        _rt_talk.save()
                                        result["successful"] += 1
                                    except Exception as e:
                                        result["false"] += 1
                                        result["error"].append(e)
                                else:
                                    result['false'] += 1
                                    result['error'].append("%s 对话的格式不对，导致无法提取" % _rt_talk_data)
                            else:
                                result['false'] += 1
                                result['error'].append("%s 对话的格式不对，导致无法提取" % _rt_talk_data)
                        else:
                            result["discard"] += 1
                    else:
                        break

                self.message_user('导入成功数据%s条' % int(result['successful']), 'success')
                if result['false'] > 0 or result['error']:
                    self.message_user('导入失败数据%s条,主要的错误是%s' % (int(result['false']), result['error']), 'warning')
                if result['discard'] > 0:
                    self.message_user('丢弃无效对话数据%s条' % int(result['discard']), 'error')
        return super(GiftInTalkPenddingAdmin, self).post(request, *args, **kwargs)

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(GiftInTalkPenddingAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0, platform=self.request.user.platform)
        return queryset


class GiftInTalkRepeatAdmin(object):
    list_display = ['order_status', 'nickname', 'cs_information', 'goods', 'order_id', 'mistakes', 'platform',
                    'order_category', 'servicer', 'creator']
    list_filter = ['mistakes', 'create_time', 'creator', 'order_category']
    list_editable = ['goods', 'nickname', 'order_id', 'cs_information']
    search_fields = ['nickname', 'order_id']

    actions = [SubmitGiftAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(GiftInTalkRepeatAdmin, self).queryset()
        repeat_nicks = queryset.filter(mistakes__in=[1, 2], order_status=1).values('nickname')
        nicks_lis = []
        for i in repeat_nicks:
            nicks_lis.append(i['nickname'])
        queryset = queryset.filter(nickname__in=nicks_lis, order_status__in=[1, 2], platform=self.request.user.platform).order_by("-nickname")

        return queryset

# 对话信息查询
class GiftInTalkAdmin(object):
    list_display = ['platform', 'order_category', 'servicer', 'order_status', 'goods', 'nickname', 'order_id', 'cs_information']
    list_filter = ['creator', 'platform', 'create_time', 'update_time', 'order_status', 'order_category']
    search_fields = ['nickname', 'order_id']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 赠品订单处理
class GiftOrderPenddingAdmin(object):
    list_display = ['shop', 'nickname', 'receiver', 'address', 'mobile', 'd_condition', 'discount', 'post_fee',
                    'receivable', 'goods_price', 'total_prices', 'goods_id', 'goods_name', 'quantity', 'category',
                    'buyer_remark', 'cs_memoranda', 'province', 'city', 'district']
    list_filter = ['creator', 'update_time', 'shop', 'quantity', 'district', 'order_category']
    search_fields = ['nickname', 'mobile', 'order_id']
    actions = [SubmitAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(GiftOrderPenddingAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 赠品订单查询
class GiftOrderInfoAdmin(object):
    list_display = ['shop', 'nickname', 'receiver', 'address', 'mobile', 'd_condition', 'discount', 'post_fee',
                    'receivable', 'goods_price', 'total_prices', 'goods_id', 'goods_name', 'quantity', 'category',
                    'buyer_remark', 'cs_memoranda', 'province', 'city', 'district']
    list_filter = ['creator', 'update_time', 'order_status', 'city', 'district', 'order_category']
    search_fields = ['nickname', 'mobile', 'order_id']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 赠品导入单据处理
class GiftImportPenddingAdmin(object):
    list_display = ['erp_order_id', 'shop', 'nickname', 'receiver', 'address', 'mobile', 'd_condition', 'discount', 'post_fee',
                    'receivable', 'goods_price', 'total_prices', 'goods_id', 'goods_name', 'quantity', 'category',
                    'buyer_remark', 'cs_memoranda', 'province', 'city', 'district']
    list_filter = ['creator', 'create_time', 'shop']
    search_fields = ['nickname', 'mobile', 'order_id']
    actions = [SubmitImportAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(GiftImportPenddingAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 赠品导入单据查询
class GiftImportAdmin(object):
    list_display = ['erp_order_id', 'shop', 'nickname', 'receiver', 'address', 'mobile', 'd_condition', 'discount', 'post_fee',
                    'receivable', 'goods_price', 'total_prices', 'goods_id', 'goods_name', 'quantity', 'category',
                    'buyer_remark', 'cs_memoranda', 'province', 'city', 'district']
    list_filter = ['creator', 'update_time']
    search_fields = ['nickname', 'mobile', 'order_id']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(GiftInTalkPendding, GiftInTalkPenddingAdmin)
xadmin.site.register(GiftInTalkRepeat, GiftInTalkRepeatAdmin)
xadmin.site.register(GiftInTalkInfo, GiftInTalkAdmin)
xadmin.site.register(GiftOrderPendding, GiftOrderPenddingAdmin)
xadmin.site.register(GiftOrderInfo, GiftOrderInfoAdmin)
xadmin.site.register(GiftImportPendding, GiftImportPenddingAdmin)
xadmin.site.register(GiftImportInfo, GiftImportAdmin)