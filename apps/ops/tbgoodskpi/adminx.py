# -*- coding: utf-8 -*-
# @Time    : 2019/7/20 15:42
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

from django.core.exceptions import PermissionDenied
import pandas as pd
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext



from .models import OriTMGoodsKPI
from apps.base.shop.models import ShopInfo


class OriTMGoodsKPIAdmin(object):
    INIT_FIELDS_DIC = {
        "统计日期": "statistical_time",
        "商品ID": "goods_id",
        "商品名称": "goods_name",
        "PC端曝光量": "pc_exposure",
        "访客数": "unique_visitor",
        "无线端访客数": "mobile_unique_visitor",
        "PC端点击次数": "pc_click_number",
        "详情页跳出率": "detail_page_bounce_rate",
        "PC端详情页跳出率": "pc_detail_page_bounce_rate",
        "无线端详情页跳出率": "mobile_detail_page_bounce_rate",
        "平均停留时长": "avg_stay_time",
        "无线端平均停留时长": "mobile_avg_stay_time",
        "PC端平均停留时长": "pc_avg_stay_time",
        "支付金额": "payment_amount",
        "PC端访客数": "pc_unique_visitor",
        "加购件数": "shopping_goods",
        "PC端加购件数": "pc_shopping_goods",
        "无线端加购件数": "mobile_shopping_goods",
        "商品收藏买家数": "product_favorite_buyers",
        "PC端商品收藏买家数": "pc_product_favorite_buyers",
        "无线端商品收藏买家数": "mobile_product_favorite_buyers",
        "PC端支付金额": "pc_payment_amount",
        "无线端支付金额": "mobile_payment_amount",
        "支付件数": "payment_quantity",
        "PC端支付件数": "pc_payment_quantity",
        "无线端支付件数": "mobile_payment_quantity",
        "支付买家数": "payment_buyers",
        "PC端支付买家数": "pc_payment_buyers",
        "无线端支付买家数": "mobile_payment_buyers",
        "客单价": "per_customer_transaction",
        "PC端客单价": "pc_per_customer_transaction",
        "无线端客单价": "mobile_per_customer_transaction",
        "支付转化率": "payment_conversion_rate",
        "PC端支付转化率": "pc_payment_conversion_rate",
        "无线端支付转化率": "mobile_payment_conversion_rate",
        "商品浏览量": "goods_views",
        "无线端商品浏览量": "mobile_goods_views",
        "PC端商品浏览量": "pc_goods_views",
        "成功退款退货金额": "refund_amount",
        "下单买家数": "order_buyers",
        "下单件数": "order_quantity",
        "下单金额": "order_amount",
        "店铺": "shopping_goods",
        "单据状态": "status"
    }
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    import_data = True

    def post(self, request, *args, **kwargs):
        creator = request.user.username
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(file, creator)
            self.message_user('导入成功数据%s条' % result['successful'], 'success')
            if result['false'] > 0:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (result['false'], result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('重复数据%s条' % result['repeated'], 'error')

        return super(OriTMGoodsKPIAdmin, self).post(request, args, kwargs)

    def handle_upload_file(self, _file, creator):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            with pd.ExcelFile(_file) as xls:
                df = pd.read_excel(xls, sheet_name=0)
                _pre_shop = df.iloc[1, 0]
                shop_name = _pre_shop.split("：")
                if len(shop_name) == 2:
                    shop_name = shop_name[-1]
                    if ShopInfo.objects.filter(shop_name=shop_name).exists():
                        shop = ShopInfo.objects.filter(shop_name=shop_name)[0]
                    else:
                        report_dic['false'] = 1
                        report_dic["error"] = '检查店铺是否添加，此店铺不存在系统店铺列表中'
                        return report_dic
                else:
                    report_dic['false'] = 1
                    report_dic["error"] = '检查表格是否为源表，请不要修改源表，请重新下载源表导入'
                    return report_dic

                columns = [i for i in df.iloc[6]]
                df.columns = columns
                df.drop([0, 1, 2, 3, 4, 5, 6], inplace=True)

                # 获取表头，对表头进行转换成数据库字段名
                columns_key = df.columns.values.tolist()

                for i in range(len(columns_key)):
                    columns_key[i] = columns_key[i].replace(' ', '').replace('=', '')

                for i in range(len(columns_key)):
                    if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

                # 验证一下必要的核心字段是否存在
                _ret_verify_field = OriTMGoodsKPI.verify_mandatory(columns_key)
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
                    intermediate_report_dic = self.save_resources(_ret_list, creator, shop)
                    for k, v in intermediate_report_dic.items():
                        if k == "error":
                            if intermediate_report_dic["error"]:
                                report_dic[k].append(v)
                        else:
                            report_dic[k] += v
                return report_dic
        else:
            return "只支持excel文件格式！"

    def save_resources(self, resource, creator, shop):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        # 开始导入数据
        for row in resource:
            # ERP导出文档添加了等于号，毙掉等于号。
            order = OriTMGoodsKPI()  # 创建表格每一行为一个对象
            # 清除订单号的特殊字符
            statistical_time = row['statistical_time']
            goods_id = row['goods_id']

            # 如果订单号查询，已经存在，丢弃订单，计数为重复订单
            target_order = OriTMGoodsKPI.objects.all().filter(statistical_time=statistical_time, goods_id=goods_id)
            if target_order.exists():
                report_dic["repeated"] += 1
                continue
            for k, v in row.items():
                # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
                if hasattr(order, k):
                    if str(v) in ['nan', 'NaT']:
                        pass
                    elif "%" in str(v):
                        v = float(v.split("%")[0])/100
                        setattr(order, k, v)  # 百分号的转换成浮点数保存
                    elif "," in str(v) and "." not in str(v):
                        v = int(v.replace(",", "").replace("，", ""))
                        setattr(order, k, v)  # 数字逗号取出，保存成数字
                    elif "," in str(v) and "." in str(v):
                        v = float(v.replace(",", "").replace("，", ""))
                        setattr(order, k, v)  # 数字逗号取出，保存成浮点数字
                    else:
                        setattr(order, k, v)  # 更新对象属性为字典对应键值
            order.shop = shop

            try:
                order.creator = creator
                order.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["error"].append(e)
                report_dic["false"] += 1
        return report_dic

    def queryset(self):
        qs = OriTMGoodsKPI.objects.all().filter(status=1)
        return qs

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(OriTMGoodsKPI, OriTMGoodsKPIAdmin)