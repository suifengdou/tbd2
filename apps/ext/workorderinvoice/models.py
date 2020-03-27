from django.db import models

# Create your models here.

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel

from apps.utils.geography.models import CityInfo, ProvinceInfo, DistrictInfo
from apps.base.company.models import MainInfo
from apps.base.shop.models import ShopInfo
from apps.base.goods.models import MachineInfo


class WorkOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '申请未报'),
        (2, '正在审核'),
        (3, '单据生成'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '开票中'),
        (2, '已开票'),
        (3, '待买票'),
        (4, '信息错'),
        (5, '已打单'),
        (6, '已处理'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '没开票公司'),
        (2, '货品错误'),
        (3, '专票信息缺'),
        (4, '收件手机错'),
        (5, '超限额发票'),
        (6, '递交发票订单出错'),
        (7, '生成发票货品出错'),
        (8, '单货品超限额非法'),
    )

    LOGICAL_DEXISION = (
        (0, '否'),
        (1, '是'),
    )
    CATEGORY = (
        (1, '专票'),
        (2, '普票'),
    )

    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    company = models.ForeignKey(MainInfo, on_delete=models.CASCADE, related_name='mainc', null=True, blank=True, verbose_name='收款开票公司')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='源单号')
    order_category = models.SmallIntegerField(choices=CATEGORY, verbose_name='发票类型')

    title = models.CharField(max_length=150, verbose_name='发票抬头')
    tax_id = models.CharField(max_length=60, verbose_name='纳税人识别号')
    phone = models.CharField(null=True, blank=True, max_length=60, verbose_name='联系电话')
    bank = models.CharField(null=True, blank=True, max_length=100, verbose_name='银行名称')
    account = models.CharField(null=True, blank=True, max_length=60, verbose_name='银行账户')
    address = models.CharField(null=True, blank=True, max_length=200, verbose_name='地址')
    remark = models.CharField(null=True, blank=True, max_length=230, verbose_name='发票备注')

    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机')
    sent_city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='收件城市')
    sent_district = models.CharField(max_length=30, verbose_name='收件区县')
    sent_address = models.CharField(max_length=200, verbose_name='收件地址')

    amount = models.FloatField(default=0, verbose_name='申请税前开票总额')

    is_deliver = models.SmallIntegerField(choices=LOGICAL_DEXISION, verbose_name='是否打印快递')

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='申请提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='开票处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='开票处理间隔(分钟)')

    message = models.CharField(null=True, blank=True, max_length=300, verbose_name='工单留言')
    memorandum = models.CharField(null=True, blank=True, max_length=300, verbose_name='工单反馈')

    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态')

    class Meta:
        verbose_name = 'EXT-发票工单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_workorder_invoice'

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


class WOUnhandle(WorkOrder):
    class Meta:
        verbose_name = 'EXT-发票工单-未递交'
        verbose_name_plural = verbose_name
        proxy = True


class WOCheck(WorkOrder):
    class Meta:
        verbose_name = 'EXT-发票工单-未审核'
        verbose_name_plural = verbose_name
        proxy = True


class GoodsDetail(BaseModel):

    invoice = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, verbose_name='发票工单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='含税单价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')


    class Meta:
        verbose_name = 'EXT-发票工单-货品明细'
        verbose_name_plural = verbose_name
        unique_together = (('invoice', 'goods_name'))
        db_table = 'ext_workorder_invoice_goods'

    def __str__(self):
        return self.invoice.order_id


class InvoiceOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '开票处理'),
        (2, '终审复核'),
        (3, '工单完结'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '开票中'),
        (2, '已开票'),
        (3, '待买票'),
        (4, '信息错'),
        (5, '已打单'),
        (6, '已处理'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '返回单号为空'),
        (2, '处理意见为空'),
        (3, '经销商反馈为空'),
        (4, '先标记为已处理才能审核'),
        (5, '先标记为已对账才能审核'),
        (6, '工单必须为取消状态'),
        (7, '先标记为终端清才能审核'),
    )

    LOGICAL_DEXISION = (
        (0, '否'),
        (1, '是'),
    )
    CATEGORY = (
        (1, '专票'),
        (2, '普票'),
    )

    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, verbose_name='来源单号')
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    company = models.ForeignKey(MainInfo, on_delete=models.CASCADE, related_name='mainc_invoice', null=True, blank=True, verbose_name='收款开票公司')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='源单号')
    order_category = models.SmallIntegerField(choices=CATEGORY, verbose_name='发票类型')
    invoice_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='发票号码')

    title = models.CharField(max_length=150, verbose_name='发票抬头')
    tax_id = models.CharField(max_length=60, verbose_name='纳税人识别号')
    phone = models.CharField(null=True, blank=True, max_length=60, verbose_name='联系电话')
    bank = models.CharField(null=True, blank=True, max_length=100, verbose_name='银行名称')
    account = models.CharField(null=True, blank=True, max_length=60, verbose_name='银行账户')
    address = models.CharField(null=True, blank=True, max_length=200, verbose_name='地址')
    remark = models.CharField(null=True, blank=True, max_length=230, verbose_name='发票备注')

    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机')
    sent_province = models.ForeignKey(ProvinceInfo, on_delete=models.CASCADE, verbose_name='收件省份')
    sent_city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='收件城市')
    sent_district = models.CharField(max_length=30, verbose_name='收件区县')
    sent_address = models.CharField(max_length=200, verbose_name='收件地址')

    amount = models.FloatField(verbose_name='发票税前开票总额')
    ori_amount = models.FloatField(verbose_name='源工单开票总额')

    is_deliver = models.SmallIntegerField(choices=LOGICAL_DEXISION, verbose_name='是否打印快递')
    track_no = models.CharField(null=True, blank=True, max_length=60, verbose_name='快递单号')

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='申请提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='开票处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='开票处理间隔(分钟)')

    message = models.CharField(null=True, blank=True, max_length=300, verbose_name='工单留言')
    memorandum = models.CharField(null=True, blank=True, max_length=300, verbose_name='工单反馈')

    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态')

    class Meta:
        verbose_name = 'EXT-发票订单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_invoice_order'

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


class IOhandle(InvoiceOrder):
    class Meta:
        verbose_name = 'EXT-发票订单-未开票'
        verbose_name_plural = verbose_name
        proxy = True


class IOCheck(InvoiceOrder):
    class Meta:
        verbose_name = 'EXT-发票订单-未终审'
        verbose_name_plural = verbose_name
        proxy = True


class InvoiceGoods(BaseModel):

    invoice = models.ForeignKey(InvoiceOrder, on_delete=models.CASCADE, verbose_name='发票订单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='含税单价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    class Meta:
        verbose_name = 'EXT-发票订单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_invoice_order_goods'

    def __str__(self):
        return self.invoice.order_id