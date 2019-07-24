# -*- coding: utf-8 -*-
# @Time    : 2019/7/20 15:51
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm


import xadmin


from .models import WWFilterationInfo, WWReceptionInfo, WWNoReplayInfo, WWDialogueListInfo


class WWFilterationInfoAdmin(object):
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
    pass


class WWReceptionInfoAdmin(object):
    pass


class WWNoReplayInfoAdmin(object):
    pass


class WWDialogueListInfoAdmin(object):
    pass


xadmin.site.register(WWFilterationInfo, WWFilterationInfoAdmin)
xadmin.site.register(WWReceptionInfo, WWReceptionInfoAdmin)
xadmin.site.register(WWNoReplayInfo, WWNoReplayInfoAdmin)
xadmin.site.register(WWDialogueListInfo, WWDialogueListInfoAdmin)
