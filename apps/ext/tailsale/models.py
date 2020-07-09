from django.db import models

# Create your models here.

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel

from apps.utils.geography.models import CityInfo, ProvinceInfo, DistrictInfo
from apps.base.company.models import MainInfo, CompanyInfo
from apps.base.shop.models import ShopInfo
from apps.base.goods.models import MachineInfo
from apps.base.department.models import DepartmentInfo


class OriTailOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '申请未报'),
        (2, '正在审核'),
        (3, '单据生成'),
        (4, '发货完成'),
        (5, '结算完成'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '驳回'),
        (6, '物流订单'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '账号未设置公司'),
        (2, '货品金额是零'),
        (3, '收件人手机错误'),
        (4, '单号不符合规则'),
        (5, '需要选择拆弹发货'),
        (6, '递交订单出错'),
        (7, '生成订单货品出错'),
    )

    LOGICAL_DECISION = (
        (0, '否'),
        (1, '是'),
    )
    CATEGORY = (
        (1, '销售订单'),
        (2, '售后换货'),
    )

    MODE_W = (
        (0, '翻新回流'),
        (1, '二手在库'),
    )

    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='源单号')
    order_category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='订单类型')
    mode_warehouse = models.SmallIntegerField(choices=MODE_W, default=0, verbose_name='发货模式')
    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机')
    sent_city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='收件城市')
    sent_district = models.CharField(null=True, blank=True, max_length=30, verbose_name='收件区县')
    sent_address = models.CharField(max_length=200, verbose_name='收件地址')
    amount = models.FloatField(default=0, verbose_name='尾货订单总价')
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='处理间隔(分钟)')

    message = models.TextField(null=True, blank=True, verbose_name='订单留言')
    feedback = models.TextField(null=True, blank=True, verbose_name='订单反馈')

    sign_company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='ori_tail_company',
                                     null=True, blank=True, verbose_name='创建公司')
    sign_department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE, related_name='ori_tail_department',
                                        null=True, blank=True, verbose_name='创建部门')

    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='订单状态')

    class Meta:
        verbose_name = 'EXT-原始尾货订单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_ori_tailorder'

    def __str__(self):
        return self.order_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ['order_id', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address',
                        'is_deliver', 'message', 'goods_id', 'goods_name', 'quantity', 'price']

        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class OTOUnhandle(OriTailOrder):
    class Meta:
        verbose_name = 'EXT-原始尾货订单-未递交'
        verbose_name_plural = verbose_name
        proxy = True


class OTOCheck(OriTailOrder):
    class Meta:
        verbose_name = 'EXT-原始尾货订单-未审核'
        verbose_name_plural = verbose_name
        proxy = True


class OTOGoods(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '正常'),
    )

    ori_tail_order = models.ForeignKey(OriTailOrder, on_delete=models.CASCADE, verbose_name='原始尾货订单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='含税单价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='货品状态')

    class Meta:
        verbose_name = 'EXT-原始尾货订单-货品明细'
        verbose_name_plural = verbose_name
        unique_together = (('ori_tail_order', 'goods_name'))
        db_table = 'ext_ori_tailorder_goods'

    def __str__(self):
        return self.ori_tail_order.order_id

    def amount(self):
        try:
            amount = self.price * self.quantity
        except:
            amount = 0
        return amount
    amount.short_description = '货品总价'

    def sent_consignee(self):
        sent_consignee = self.ori_tail_order.sent_consignee
        return sent_consignee
    sent_consignee.short_description = '收货人'

    def sent_smartphone(self):
        sent_smartphone = self.ori_tail_order.sent_smartphone
        return sent_smartphone
    sent_smartphone.short_description = '手机'

    def sent_address(self):
        sent_address = self.ori_tail_order.sent_address
        return sent_address
    sent_address.short_description = '地址'

    def shop(self):
        shop = self.ori_tail_order.shop
        return shop
    shop.short_description = '店铺'


class TailOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '发货处理'),
        (2, '终审复核'),
        (3, '工单完结'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '无发票号'),
        (2, '快递单错误'),
        (3, '快递未发货'),
        (4, '驳回出错'),

    )

    LOGICAL_DEXISION = (
        (0, '否'),
        (1, '是'),
    )
    CATEGORY = (
        (1, '销售订单'),
        (2, '售后换货'),
    )
    MODE_W = (
        (0, '翻新回流'),
        (1, '二手在库'),
    )

    ori_tail_order = models.ForeignKey(OriTailOrder, on_delete=models.CASCADE, verbose_name='来源单号')
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='源单号')
    order_category = models.SmallIntegerField(choices=CATEGORY, verbose_name='订单类型')
    mode_warehouse = models.SmallIntegerField(choices=MODE_W, default=0, verbose_name='发货模式')

    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机')
    sent_province = models.ForeignKey(ProvinceInfo, on_delete=models.CASCADE, verbose_name='收件省份')
    sent_city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='收件城市')
    sent_district = models.CharField(null=True, blank=True, max_length=30, verbose_name='收件区县')
    sent_address = models.CharField(max_length=200, verbose_name='收件地址')

    amount = models.FloatField(default=0, verbose_name='尾货订单总价')
    ori_amount = models.FloatField(verbose_name='源尾货订单总价')

    track_no = models.TextField(null=True, blank=True, verbose_name='快递信息')

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='申请提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='开票处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='开票处理间隔(分钟)')

    message = models.TextField(null=True, blank=True, verbose_name='工单留言')
    feedback = models.TextField(null=True, blank=True, verbose_name='工单反馈')

    sign_company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='tail_company', null=True,
                                     blank=True, verbose_name='创建公司')
    sign_department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE, related_name='tail_department',
                                        null=True, blank=True, verbose_name='创建部门')

    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='订单状态')

    class Meta:
        verbose_name = 'EXT-尾货订单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder'

    def __str__(self):
        return self.order_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ['order_id', 'information', 'category']
        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class TOhandle(TailOrder):
    class Meta:
        verbose_name = 'EXT-尾货订单-重损仓未发货'
        verbose_name_plural = verbose_name
        proxy = True


class TOSpecialhandle(TailOrder):
    class Meta:
        verbose_name = 'EXT-尾货订单-非重损未发货'
        verbose_name_plural = verbose_name
        proxy = True


class TOCheck(TailOrder):
    class Meta:
        verbose_name = 'EXT-尾货订单-未完成'
        verbose_name_plural = verbose_name
        proxy = True


class TOGoods(BaseModel):
    tail_order = models.ForeignKey(TailOrder, on_delete=models.CASCADE, verbose_name='尾货订单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='单价')
    amount = models.FloatField(verbose_name='总价')
    settlement_price = models.FloatField(null=True, blank=True, verbose_name='结算单价')
    settlement_amount = models.FloatField(null=True, blank=True, verbose_name='结算总价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    class Meta:
        verbose_name = 'EXT-尾货订单-货品明细'
        verbose_name_plural = verbose_name
        unique_together = (('tail_order', 'goods_name'))
        db_table = 'ext_tailorder_goods'

    def __str__(self):
        return self.tail_order.order_id


class RefundOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待递交'),
        (2, '待处理'),
        (3, '已完结'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '无发票号'),
        (2, '快递单错误'),
        (3, '快递未发货'),
        (4, '驳回出错'),

    )

    LOGICAL_DEXISION = (
        (0, '否'),
        (1, '是'),
    )
    CATEGORY = (
        (1, '退货退款'),
        (2, '换货'),
        (3, '仅退款'),
        (4, '维修'),
    )

    ori_tail_order = models.ForeignKey(OriTailOrder, on_delete=models.CASCADE, related_name='refund_ori_order', verbose_name='来源单号')
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='源单号')
    refund_category = models.SmallIntegerField(choices=CATEGORY, verbose_name='退款类型')

    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机')

    quantity = models.IntegerField(null=True, blank=True, verbose_name='货品数量')
    amount = models.FloatField(default=0, verbose_name='申请退款总额')
    ori_amount = models.FloatField(verbose_name='源订单总额')

    track_no = models.TextField(null=True, blank=True, verbose_name='返回快递信息')

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='申请提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='退款处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='退款处理间隔(分钟)')

    message = models.TextField(null=True, blank=True, verbose_name='工单留言')
    feedback = models.TextField(null=True, blank=True, verbose_name='工单反馈')

    sign_company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='re_tail_company', null=True,
                                     blank=True, verbose_name='创建公司')
    sign_department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE, related_name='re_tail_department',
                                        null=True, blank=True, verbose_name='创建部门')
    info_refund = models.TextField(null=True, blank=True, verbose_name='退款信息结果')

    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='订单状态')

    class Meta:
        verbose_name = 'EXT-尾货退换单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_refund'

    def __str__(self):
        return self.order_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ['order_id', 'information', 'category']
        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class ROHandle(RefundOrder):
    class Meta:
        verbose_name = 'EXT-尾货退换单-待递交'
        verbose_name_plural = verbose_name
        proxy = True


class ROCheck(RefundOrder):
    class Meta:
        verbose_name = 'EXT-尾货退换单-待入库'
        verbose_name_plural = verbose_name
        proxy = True


class ROGoods(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '正常'),
    )
    refund_order = models.ForeignKey(RefundOrder, on_delete=models.CASCADE, verbose_name='退款订单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='含税单价')
    amount = models.FloatField(verbose_name='货品总价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='货品状态')

    class Meta:
        verbose_name = 'EXT-尾货订单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_refund_goods'

    def __str__(self):
        return self.refund_order.order_id


class PayBillOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待支付'),
        (2, '待结算'),
        (3, '已完成'),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '未打印'),
        (2, '快递信息回写失败'),

    )
    MODE_W = (
        (0, '翻新回流'),
        (1, '二手在库'),
    )
    CATEGORY = (
        (1, '销售订单'),
        (2, '售后换货'),
    )
    tail_order = models.ForeignKey(TailOrder, on_delete=models.CASCADE, related_name='ori_order',
                                   verbose_name='来源单号')
    order_category = models.SmallIntegerField(choices=CATEGORY, verbose_name='订单类型')
    mode_warehouse = models.SmallIntegerField(choices=MODE_W, default=0, verbose_name='发货模式')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='结算单号')
    quantity = models.IntegerField(verbose_name='货品总数')
    amount = models.FloatField(verbose_name='结算金额')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'EXT-尾货订单结算单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_paybill'

    def __str__(self):
        return self.order_id


class PBOCheck(RefundOrder):
    class Meta:
        verbose_name = 'EXT-尾货退换单-待结算'
        verbose_name_plural = verbose_name
        proxy = True


class PBOGoods(BaseModel):
    pb_order = models.ForeignKey(PayBillOrder, on_delete=models.CASCADE, verbose_name='结算订单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='含税单价')
    amount = models.FloatField(verbose_name='货品总价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    class Meta:
        verbose_name = 'EXT-尾货订单结算单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_paybill_goods'

    def __str__(self):
        return self.pb_order.order_id


class ArrearsBillOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待支付'),
        (2, '待结算'),
        (3, '已完成'),
    )
    PROCESS_TAG = (
        (0, '待打印'),
        (1, '已打印'),
        (2, '暂停发'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '未打印'),
        (2, '快递信息回写失败'),

    )
    MODE_W = (
        (0, '翻新回流'),
        (1, '二手在库'),
    )
    CATEGORY = (
        (1, '退货退款'),
        (2, '换货'),
        (3, '仅退款'),
    )
    refund_order = models.ForeignKey(RefundOrder, on_delete=models.CASCADE, verbose_name='退款来源单号')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='结算单号')
    order_category = models.SmallIntegerField(choices=CATEGORY, verbose_name='订单类型')
    quantity = models.IntegerField(verbose_name='货品总数')
    amount = models.FloatField(verbose_name='退款结算金额')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'EXT-尾货退款结算单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_arrearsbill'

    def __str__(self):
        return self.order_id


class ABOGoods(BaseModel):
    ab_order = models.ForeignKey(ArrearsBillOrder, on_delete=models.CASCADE, verbose_name='退款订单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='含税单价')
    amount = models.FloatField(verbose_name='货品总价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    class Meta:
        verbose_name = 'EXT-尾货退款结算单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_arrearsbill_goods'

    def __str__(self):
        return self.ab_order.order_id


class FinalStatement(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待支付'),
        (2, '待结算'),
        (3, '已完成'),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
    )
    MISTAKE_LIST = (
        (0, '正常'),

    )
    MODE_W = (
        (0, '翻新回流'),
        (1, '二手在库'),
    )
    order_id = models.CharField(unique=True, max_length=100, verbose_name='账单单号')
    pay_order_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='付款单号')
    quantity = models.IntegerField(verbose_name='货品数量')
    amount = models.FloatField(verbose_name='结算金额')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')


    class Meta:
        verbose_name = 'EXT-尾货退款结算单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_final'


class FinalStatementGoods(BaseModel):
    CATEGORY = (
        (1, '销售收入'),
        (2, '退货退款'),
    )
    account_order = models.ForeignKey(FinalStatement, on_delete=models.CASCADE, verbose_name='结算单号')
    order_category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='结算类型')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='含税单价')
    amount = models.FloatField(verbose_name='货品总价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    class Meta:
        verbose_name = 'EXT-尾货退款结算单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_final_goods'

    def __str__(self):
        return self.account_order.order_id


class AccountInfo(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待支付'),
        (2, '待结算'),
        (3, '已完成'),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
    )
    MISTAKE_LIST = (
        (0, '正常'),

    )
    CATEGORY = (
        (1, '收入'),
        (2, '退货'),
    )
    MODE_W = (
        (0, '翻新回流'),
        (1, '二手在库'),
    )

    order_id = models.CharField(unique=True, max_length=100, verbose_name='账单单号')
    pay_order_id = models.CharField(max_length=100, verbose_name='付款单号')
    order_category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='结算类型')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='含税单价')
    amount = models.FloatField(verbose_name='货品总价')

    final_statement = models.ForeignKey(FinalStatement, on_delete=models.CASCADE, null=True, blank=True,
                                        verbose_name='结算单')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'EXT-尾货对账单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_account'