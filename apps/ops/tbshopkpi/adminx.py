# -*- coding: utf-8 -*-
# @Time    : 2019/7/5 8:59
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import pandas as pd
import xadmin


from .models import OriTMShopKPI
from apps.base.shop.models import ShopInfo


class OriTMShopKPIAdmin(object):
    INIT_FIELDS_DIC = {
        "统计日期": "statistical_time",
        "PC端访客数": "pc_unique_visitor",
        "PC端浏览量": "pc_page_views",
        "访客数": "unique_visitor",
        "无线端访客数": "mobile_unique_visitor",
        "浏览量": "page_views",
        "无线端浏览量": "mobile_page_views",
        "商品访客数": "product_unique_visitor",
        "无线端商品访客数": "mobile_product_unique_visitor",
        "PC端商品访客数": "pc_product_unique_visitor",
        "商品浏览量": "product_page_views",
        "无线端商品浏览量": "mobile_product_page_views",
        "PC端商品浏览量": "pc_product_page_views",
        "平均停留时长": "avg_stay_time",
        "无线端平均停留时长": "mobile_avg_stay_time",
        "PC端平均停留时长": "pc_avg_stay_time",
        "跳失率": "bounce_rate",
        "无线端跳失率": "mobile_bounce_rate",
        "PC端跳失率": "pc_bounce_rate",
        "商品收藏买家数": "product_favorite_buyers",
        "无线端商品收藏买家数": "mobile_product_favorite_buyers",
        "PC端商品收藏买家数": "pc_product_favorite_buyers",
        "商品收藏次数": "favorite_number",
        "无线端商品收藏次数": "mobile_favorite_number",
        "PC端商品收藏次数": "pc_favorite_number",
        "加购人数": "shopping_buyers",
        "无线端加购人数": "mobile_shopping_buyers",
        "PC端加购人数": "pc_shopping_buyers",
        "支付金额": "payment_amount",
        "PC端支付金额": "pc_payment_amount",
        "无线端支付金额": "mobile_payment_amount",
        "支付买家数": "payment_buyers",
        "PC端支付买家数": "pc_payment_buyers",
        "无线端支付买家数": "mobile_payment_buyers",
        "支付子订单数": "payment_suborder",
        "PC端支付子订单数": "pc_payment_suborder",
        "无线端支付子订单数": "mobile_payment_suborder",
        "支付件数": "payment_quantity",
        "PC端支付件数": "pc_payment_quantity",
        "无线端支付件数": "mobile_payment_quantity",
        "下单金额": "order_amount",
        "PC端下单金额": "pc_order_amount",
        "无线端下单金额": "mobile_order_amount",
        "下单买家数": "order_buyers",
        "PC端下单买家数": "pc_order_buyers",
        "无线端下单买家数": "mobile_order_buyers",
        "下单件数": "order_quantity",
        "PC端下单件数": "pc_order_quantity",
        "无线端下单件数": "mobile_order_quantity",
        "人均浏览量": "avg_page_views",
        "PC端人均浏览量": "pc_avg_page_views",
        "无线端人均浏览量": "mobile_avg_page_views",
        "下单转化率": "order_conversion_rate",
        "PC端下单转化率": "pc_order_conversion_rate",
        "无线端下单转化率": "mobile_order_conversion_rate",
        "支付转化率": "payment_conversion_rate",
        "PC端支付转化率": "pc_payment_conversion_rate",
        "无线端支付转化率": "mobile_payment_conversion_rate",
        "客单价": "per_customer_transaction",
        "PC端客单价": "pc_per_customer_transaction",
        "无线端客单价": "mobile_per_customer_transaction",
        "UV价值": "uv_value",
        "PC端UV价值": "pc_uv_value",
        "无线端UV价值": "mobile_uv_value",
        "老访客数": "repeat_visitor",
        "新访客数": "new_visitor",
        "无线端老访客数": "mobile_repeat_visitor",
        "无线端新访客数": "mobile_new_visitor",
        "PC端老访客数": "pc_repeat_visitor",
        "PC端新访客数": "pc_new_visitor",
        "加购件数": "shopping_goods",
        "PC端加购件数": "pc_shopping_goods",
        "无线端加购件数": "mobile_shopping_goods",
        "支付老买家数": "payment_repeat_visitor",
        "PC端支付老买家数": "pc_payment_repeat_visitor",
        "无线端支付老买家数": "mobile_payment_repeat_visitor",
        "老买家支付金额": "amount_repeat_visitor",
        "直通车消耗": "fee_through_train",
        "钻石展位消耗": "cost_per_thousand",
        "淘宝客佣金": "commission_promoter",
        "成功退款金额": "refund_amount",
        "评价数": "comment",
        "有图评价数": "has_photograph_comment",
        "正面评价数": "positive_comment",
        "负面评价数": "negative_comment",
        "老买家正面评价数": "repeat_visitor_positive_comment",
        "老买家负面评价数": "repeat_visitor_negative_comment",
        "支付父订单数": "payment_parents_order",
        "揽收包裹数": "packages_collect",
        "发货包裹数": "packages_delivering",
        "派送包裹数": "packages_delivered",
        "签收成功包裹数": "packages_sign",
        "平均支付_签收时长(秒)": "avg_trading_time",
        "描述相符评分": "description_points",
        "物流服务评分": "delivery_points",
        "服务态度评分": "service_points",
        "下单-支付转化率": "order_payment_conversion_rate",
        "PC端下单-支付转化率": "pc_order_payment_conversion_rate",
        "无线端下单-支付转化率": "mobile_order_payment_conversion_rate",
        "支付商品数": "goods_paid",
        "PC端支付商品数": "pc_goods_paid",
        "无线端支付商品数": "mobile_goods_paid",
        "店铺收藏买家数": "shop_favorite_buyers",
        "PC端店铺收藏买家数": "pc_shop_favorite_buyers",
        "无线端店铺收藏买家数": "mobile_shop_favorite_buyers",
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

        return super(OriTMShopKPIAdmin, self).post(request, args, kwargs)

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
                _ret_verify_field = OriTMShopKPI.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    report_dic['false'] = 1
                    report_dic["error"] = _ret_verify_field
                    return report_dic

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
            order = OriTMShopKPI()  # 创建表格每一行为一个对象
            # 清除订单号的特殊字符
            statistical_time = row['statistical_time']

            # 如果订单号查询，已经存在，丢弃订单，计数为重复订单
            target_order = OriTMShopKPI.objects.all().filter(statistical_time=statistical_time)
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
        qs = OriTMShopKPI.objects.all().filter(status=1)
        return qs

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(OriTMShopKPI, OriTMShopKPIAdmin)