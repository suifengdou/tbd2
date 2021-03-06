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
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '驳回'),
        (6, '物流订单'),
        (7, '部分发货'),
        (8, '重损发货'),
        (9, '非重损发货'),
        (10, '特殊发货'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '账号未设置公司'),
        (2, '货品金额是零'),
        (3, '收件人手机错误'),
        (4, '单号不符合规则'),
        (5, '需要选择拆单发货'),
        (6, '递交订单出错'),
        (7, '生成订单货品出错'),
        (8, '货品数量错误'),
        (9, '重复生成订单，联系管理员'),
        (10, '重复生成订单，联系管理员'),
        (11, '生成订单货品出错，联系管理员'),
        (12, '发货仓库和单据类型不符'),
        (13, '订单货品导入出错'),
        (14, '导入货品编码错误'),
        (15, '重复订单'),
        (16, '型号错误'),
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
        (0, '回流'),
        (1, '二手'),
    )

    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='源单号', db_index=True)
    order_category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='订单类型')
    mode_warehouse = models.SmallIntegerField(choices=MODE_W, default=0, verbose_name='发货模式')
    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机')
    sent_city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='收件城市')
    sent_district = models.CharField(null=True, blank=True, max_length=30, verbose_name='收件区县')
    sent_address = models.CharField(max_length=200, verbose_name='收件地址')

    amount = models.FloatField(default=0, verbose_name='尾货订单总价')
    quantity = models.IntegerField(default=0, verbose_name='货品总数')
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
        return str(self.order_id)

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ['shop', 'order_id', 'order_category', 'mode_warehouse', 'sent_consignee',
                        'sent_smartphone', 'sent_city', 'sent_district', 'sent_address',
                        'message', 'goods_id', 'quantity', 'price']

        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None

    def goods_name(self):
        goods_name = self.otogoods_set.all()
        if len(goods_name) == 1:
            goods_name = goods_name[0].goods_name.goods_name
        elif len(goods_name) > 1:
            goods_name = '多种'
        else:
            goods_name = '无'
        return goods_name
    goods_name.short_description = '单据货品'



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
    price = models.FloatField(verbose_name='单价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='货品状态')

    class Meta:
        verbose_name = 'EXT-原始尾货订单-货品明细'
        verbose_name_plural = verbose_name
        unique_together = (('ori_tail_order', 'goods_name'))
        db_table = 'ext_ori_tailorder_goods'

    def __str__(self):
        return self.ori_tail_order.order_id

    ori_tail_order.short_description = '原始单号'

    def nickname(self):
        nickname = self.sent_consignee()
        return nickname
    nickname.short_description = '网名'

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
    shop.short_description = '店铺名称'


class TailOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '发货处理'),
        (2, '发货完成'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '驳回'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '快递单号错误'),
        (2, '重复递交'),
        (3, '结算单保存出错'),
        (4, '结算单货品保存出错'),

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
        (0, '回流'),
        (1, '二手'),
    )

    ori_tail_order = models.ForeignKey(OriTailOrder, on_delete=models.CASCADE, verbose_name='来源单号')
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='尾货订单', db_index=True)
    order_category = models.SmallIntegerField(choices=CATEGORY, verbose_name='订单类型')
    mode_warehouse = models.SmallIntegerField(choices=MODE_W, default=0, verbose_name='发货模式')

    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机')
    sent_province = models.ForeignKey(ProvinceInfo, on_delete=models.CASCADE, verbose_name='收件省份')
    sent_city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='收件城市')
    sent_district = models.CharField(null=True, blank=True, max_length=30, verbose_name='收件区县')
    sent_address = models.CharField(max_length=200, verbose_name='收件地址')

    amount = models.FloatField(default=0, verbose_name='尾货订单总价')
    quantity = models.IntegerField(default=0, verbose_name='货品总数')
    ori_amount = models.FloatField(verbose_name='源尾货订单总价')

    track_no = models.CharField(max_length=150, null=True, blank=True, verbose_name='快递信息')

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='处理间隔(分钟)')

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
        return str(self.order_id)

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ['order_id', 'track_no']
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


class TOGoods(BaseModel):
    tail_order = models.ForeignKey(TailOrder, on_delete=models.CASCADE, verbose_name='尾货订单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='单价')
    amount = models.FloatField(verbose_name='总价')
    settlement_price = models.FloatField(null=True, blank=True, verbose_name='结算单价')
    settlement_amount = models.FloatField(null=True, blank=True, verbose_name='结算总价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    class Meta:
        verbose_name = 'EXT-尾货订单-货品明细'
        verbose_name_plural = verbose_name
        unique_together = (['tail_order', 'goods_name'])
        db_table = 'ext_tailorder_goods'

    def __str__(self):
        return str(self.tail_order.order_id)

    def deliver_condition(self):
        return '款到发货'
    deliver_condition.short_description = '发货条件'

    def discounts(self):
        return 0
    discounts.short_description = '优惠金额'

    def post_fee(self):
        return 0
    post_fee.short_description = '邮费'

    def receivable(self):
        return self.settlement_amount
    receivable.short_description = '应收合计'

    def order_category(self):
        return '线下零售'
    order_category.short_description = '订单类别'

    def track_no(self):
        track_no = self.tail_order.track_no
        return track_no
    track_no.short_description = '快递信息'

    def sent_consignee(self):
        sent_consignee = self.tail_order.sent_consignee
        return sent_consignee
    sent_consignee.short_description = '收件人'

    def sent_smartphone(self):
        sent_smartphone = self.tail_order.sent_smartphone
        return sent_smartphone
    sent_smartphone.short_description = '手机'

    def sent_phone(self):
        return ''
    sent_phone.short_description = '固话'

    def sent_address(self):
        sent_address = self.tail_order.sent_address
        return sent_address
    sent_address.short_description = '地址'

    def shop(self):
        shop = self.tail_order.shop
        return shop
    shop.short_description = '店铺名称'

    def sent_province(self):
        sent_province = self.tail_order.sent_province
        return sent_province
    sent_province.short_description = '省'

    def sent_city(self):
        sent_city = self.tail_order.sent_city
        return sent_city
    sent_city.short_description = '市'

    def sent_district(self):
        sent_district = self.tail_order.sent_district
        return sent_district
    sent_district.short_description = '区'

    def mode_warehouse(self):
        mode_warehouse = self.tail_order.mode_warehouse
        MODE_W = {0: '回流', 1: '二手'}
        mode_warehouse = MODE_W[mode_warehouse]
        return mode_warehouse
    mode_warehouse.short_description = '发货模式'

    def message(self):
        message = self.tail_order.message
        return message
    message.short_description = '买家备注'

    def order_status(self):
        order_status = self.tail_order.order_status
        status_list = {0: '已被取消', 1: '发货处理', 2: '发货完成'}
        return status_list[order_status]
    order_status.short_description = '订单状态'

    def submit_time(self):
        submit_time = self.tail_order.submit_time
        return submit_time
    submit_time.short_description = '提交时间'

    def handle_time(self):
        handle_time = self.tail_order.handle_time
        return handle_time
    handle_time.short_description = '处理时间'

    def handle_interval(self):
        handle_interval = self.tail_order.handle_interval
        return handle_interval
    handle_interval.short_description = '处理间隔(分钟)'

    def refund_status(self):
        _q_refund_status = RefundOrder.objects.filter(tail_order=self.tail_order)
        if _q_refund_status.exists():
            return '是'
        else:
            return '否'
    refund_status.short_description = '是否退款'


class TOHGoods(TOGoods):
    class Meta:
        verbose_name = 'EXT-尾货订单-未发重损明细'
        verbose_name_plural = verbose_name
        proxy = True


class TOSGoods(TOGoods):
    class Meta:
        verbose_name = 'EXT-尾货订单-未发非重损明细'
        verbose_name_plural = verbose_name
        proxy = True


class TOPrivilegeGoods(TOGoods):
    class Meta:
        verbose_name = 'EXT-尾货订单-完整查询'
        verbose_name_plural = verbose_name
        proxy = True


class TODeliverGoods(TOGoods):
    class Meta:
        verbose_name = 'EXT-尾货订单-发货查询'
        verbose_name_plural = verbose_name
        proxy = True


# 尾货售后单
class RefundOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待递交'),
        (2, '待处理'),
        (3, '已审核'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '部分到货'),
        (6, '已到货'),
        (7, '换货'),
        (8, '驳回'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '退换数量超出原单数量'),
        (2, '退换金额超出原单金额'),
        (3, '无退货原因'),
        (4, '无返回快递单号'),
        (5, '换货单必须要先进行标记'),
        (6, '非换货单不可以标记'),
        (7, '非已到货状态不可以审核'),
        (8, '退换数量和收货数量不一致'),
        (9, '退换金额和收货金额不一致'),
        (10, '退换结算单重复'),
        (11, '生成结算单出错'),
        (12, '生成结算单货品出错'),
        (13, '关联的订单未发货'),
        (14, '不是退货单不可以审核'),
        (15, '物流单号重复'),

    )
    MODE_W = (
        (0, '回流'),
        (1, '二手'),
    )
    LOGICAL_DEXISION = (
        (0, '否'),
        (1, '是'),
    )
    CATEGORY = (
        (3, '退-退货退款'),
        (4, '退-换货退回'),
        (5, '退-仅退款'),
    )

    tail_order = models.ForeignKey(TailOrder, on_delete=models.CASCADE, related_name='refund_tail_order', verbose_name='来源单号')
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='店铺')
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True, verbose_name='退换单号', db_index=True)
    order_category = models.SmallIntegerField(choices=CATEGORY, default=3, verbose_name='退款类型')
    mode_warehouse = models.SmallIntegerField(choices=MODE_W, null=True, blank=True, verbose_name='发货模式')
    sent_consignee = models.CharField(null=True, blank=True, max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(null=True, blank=True, max_length=30, verbose_name='收件人手机')
    sent_city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='收件城市')
    sent_district = models.CharField(null=True, blank=True, max_length=30, verbose_name='收件区县')
    sent_address = models.CharField(null=True, blank=True, max_length=200, verbose_name='收件地址')

    quantity = models.IntegerField(null=True, blank=True, verbose_name='货品总数')

    amount = models.FloatField(default=0, verbose_name='申请退款总额')
    ori_amount = models.FloatField(null=True, blank=True, verbose_name='源订单总额')

    receipted_quantity = models.IntegerField(default=0, verbose_name='到货总数')
    receipted_amount = models.FloatField(default=0, verbose_name='到货退款总额')

    track_no = models.CharField(max_length=150, null=True, blank=True, verbose_name='返回快递信息')

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='申请提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='退款处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='退款处理间隔(分钟)')

    message = models.TextField(null=True, blank=True, verbose_name='工单留言')
    feedback = models.TextField(null=True, blank=True, verbose_name='工单反馈')

    sign_company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='re_tail_company', null=True,
                                     blank=True, verbose_name='创建公司')
    sign_department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE, related_name='re_tail_department',
                                        null=True, blank=True, verbose_name='创建部门')
    info_refund = models.TextField(null=True, blank=True, verbose_name='退换货信息原因')

    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='订单状态')
    fast_tag = models.SmallIntegerField(choices=LOGICAL_DEXISION, default=1, verbose_name='快捷状态')

    class Meta:
        verbose_name = 'EXT-尾货退货单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_refund'

    def __str__(self):
        return str(self.order_id)

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ['order_id', 'information', 'category']
        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None

    def goods_name(self):
        goods_name = self.rogoods_set.all()
        if len(goods_name) == 1:
            goods_name = goods_name[0].goods_name.goods_name
        elif len(goods_name) > 1:
            goods_name = '多种'
        else:
            goods_name = '无'
        return goods_name

    goods_name.short_description = '单据货品'


# 尾货退款订单待递交
class ROHandle(RefundOrder):
    class Meta:
        verbose_name = 'EXT-尾货退货单-待递交'
        verbose_name_plural = verbose_name
        proxy = True


# 尾货退款订单待递交
class ROCheck(RefundOrder):
    class Meta:
        verbose_name = 'EXT-尾货退货单-待处理'
        verbose_name_plural = verbose_name
        proxy = True


# 尾货退款订单货品明细
class ROGoods(BaseModel):
    PROCESSTAG = (
        (0, '未处理'),
        (1, '待处理'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '入库数量是0'),
        (2, '入库数和待收货数不符'),
    )
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待递交'),
        (2, '待入库'),
        (3, '部分到货'),
        (4, '已到货'),
    )
    refund_order = models.ForeignKey(RefundOrder, on_delete=models.CASCADE, verbose_name='退款订单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='退换货数量')
    receipted_quantity = models.IntegerField(verbose_name='到货数量')
    settlement_price = models.FloatField(verbose_name='结算单价')
    settlement_amount = models.FloatField(verbose_name='货品结算总价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='到货状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')

    class Meta:
        verbose_name = 'EXT-尾货退货单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_refund_goods'

    def __str__(self):
        return self.refund_order.order_id

    def track_no(self):
        sent_consignee = self.refund_order.track_no
        return sent_consignee
    track_no.short_description = '快递单号'

    def info_refund(self):
        sent_consignee = self.refund_order.info_refund
        return sent_consignee
    info_refund.short_description = '退换货信息原因'

    def message(self):
        sent_consignee = self.refund_order.message
        return sent_consignee
    message.short_description = '留言'

    def sent_consignee(self):
        sent_consignee = self.refund_order.sent_consignee
        return sent_consignee
    sent_consignee.short_description = '收货人'

    def sent_smartphone(self):
        sent_smartphone = self.refund_order.sent_smartphone
        return sent_smartphone

    sent_smartphone.short_description = '手机'

    def sent_address(self):
        sent_address = self.refund_order.sent_address
        return sent_address

    sent_address.short_description = '地址'

    def shop(self):
        shop = self.refund_order.shop
        return shop

    shop.short_description = '店铺'

    def sent_city(self):
        sent_city = self.refund_order.sent_city
        return sent_city

    sent_city.short_description = '城市'

    def sent_district(self):
        sent_district = self.refund_order.sent_district
        return sent_district

    sent_district.short_description = '区县'


# 尾货退款订单待递交
class ROGCheck(ROGoods):
    class Meta:
        verbose_name = 'EXT-尾货退货单-待收货'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单
class PayBillOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待提交'),
        (2, '待确认'),
        (3, '已审核'),
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
        (1, '生成尾货结算单重复'),
        (2, '生成尾货结算单出错'),
        (3, '重复生成结算单，联系管理员'),
        (4, '未确认可付款'),

    )
    MODE_W = (
        (0, '回流'),
        (1, '二手'),
    )
    CATEGORY = (
        (1, '销售订单'),
        (2, '售后换货'),
    )
    tail_order = models.ForeignKey(TailOrder, on_delete=models.CASCADE, related_name='ori_order',
                                   verbose_name='来源单号')
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    order_category = models.SmallIntegerField(choices=CATEGORY, verbose_name='订单类型')
    mode_warehouse = models.SmallIntegerField(choices=MODE_W, default=0, verbose_name='发货模式')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='结算单号', db_index=True)
    quantity = models.IntegerField(verbose_name='货品总数')
    amount = models.FloatField(verbose_name='结算金额')
    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机', db_index=True)
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='处理间隔(分钟)')

    message = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')
    feedback = models.CharField(null=True, blank=True, max_length=200, verbose_name='反馈')

    sign_company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='pbo_tail_company', null=True,
                                     blank=True, verbose_name='创建公司')
    sign_department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE, related_name='pbo_tail_department',
                                        null=True, blank=True, verbose_name='创建部门')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'EXT-尾货应收结算单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_paybill'

    def __str__(self):
        return str(self.order_id)

    def track_no(self):
        track_no = self.tail_order.track_no
        return track_no
    track_no.short_description = '快递信息'


# 应收结算单待审核
class PBOSubmit(PayBillOrder):
    class Meta:
        verbose_name = 'EXT-尾货应收结算单-待审核'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单待结算
class PBOCheck(PayBillOrder):
    class Meta:
        verbose_name = 'EXT-尾货应收结算单-待结算'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单货品明细
class PBOGoods(BaseModel):
    pb_order = models.ForeignKey(PayBillOrder, on_delete=models.CASCADE, verbose_name='结算订单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='数量')
    settlement_price = models.FloatField(verbose_name='结算货品单价')
    settlement_amount = models.FloatField(verbose_name='结算货品总价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    class Meta:
        verbose_name = 'EXT-尾货应收结算单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_paybill_goods'

    def __str__(self):
        return self.pb_order.order_id


# 退款结算单
class ArrearsBillOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待支付'),
        (2, '已审核'),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待处理'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '生成尾货结算单重复'),
        (2, '生成尾货结算单出错'),
        (3, '重复生成结算单，联系管理员'),
        (4, '未确认可付款'),
    )
    MODE_W = (
        (0, '回流'),
        (1, '二手'),
    )
    CATEGORY = (
        (3, '退-退货退款'),
        (4, '退-换货退回'),
        (5, '退-仅退款'),
        (6, '退-维修'),
    )
    refund_order = models.ForeignKey(RefundOrder, on_delete=models.CASCADE, verbose_name='退款来源单号')
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='店铺')
    order_id = models.CharField(unique=True, max_length=100, verbose_name='结算单号', db_index=True)
    order_category = models.SmallIntegerField(choices=CATEGORY, verbose_name='订单类型')
    mode_warehouse = models.SmallIntegerField(choices=MODE_W, null=True, blank=True, verbose_name='发货模式')
    settlement_quantity = models.IntegerField(verbose_name='结算货品总数')
    settlement_amount = models.FloatField(verbose_name='结算总金额')
    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机', db_index=True)

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='处理间隔(分钟)')

    message = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')
    feedback = models.CharField(null=True, blank=True, max_length=200, verbose_name='反馈')

    sign_company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='arr_tail_company', null=True,
                                     blank=True, verbose_name='创建公司')
    sign_department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE, related_name='arr_tail_department',
                                        null=True, blank=True, verbose_name='创建部门')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'EXT-尾货退款结算单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_arrearsbill'

    def __str__(self):
        return str(self.order_id)

    def track_no(self):
        track_no = self.refund_order.track_no
        return track_no
    track_no.short_description = '快递信息'


# 应收结算单待审核
class ABOSubmit(ArrearsBillOrder):
    class Meta:
        verbose_name = 'EXT-尾货退款结算单-待审核'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单待结算
class ABOCheck(ArrearsBillOrder):
    class Meta:
        verbose_name = 'EXT-尾货退款结算单-待结算'
        verbose_name_plural = verbose_name
        proxy = True


# 退款结算单货品明细
class ABOGoods(BaseModel):
    ab_order = models.ForeignKey(ArrearsBillOrder, on_delete=models.CASCADE, verbose_name='退款订单')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='货品简称')
    settlement_quantity = models.IntegerField(verbose_name='结算数量')
    settlement_price = models.FloatField(verbose_name='结算单价')
    settlement_amount = models.FloatField(verbose_name='结算货品总价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    class Meta:
        verbose_name = 'EXT-尾货退款结算单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_arrearsbill_goods'

    def __str__(self):
        return str(self.ab_order.order_id)


# 最终付款结算单
class FinalStatement(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待确认'),
        (2, '待支付'),
        (3, '待结算'),
        (4, '已完成'),
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
        (1, '无付款单号'),

    )
    MODE_W = (
        (0, '回流'),
        (1, '二手'),
    )
    order_id = models.CharField(unique=True, max_length=100, verbose_name='账单单号', db_index=True)
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    pay_order_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='付款单号')
    mode_warehouse = models.SmallIntegerField(choices=MODE_W, null=True, blank=True, verbose_name='发货模式')
    quantity = models.IntegerField(verbose_name='货品总数')
    amount = models.FloatField(verbose_name='账单金额')
    payee = models.CharField(max_length=90, null=True, blank=True, verbose_name='收款人')
    bank = models.CharField(max_length=90, null=True, blank=True, verbose_name='收款银行')
    account = models.CharField(max_length=90, null=True, blank=True, verbose_name='收款银行账户')

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='处理间隔(分钟)')

    message = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')
    feedback = models.CharField(null=True, blank=True, max_length=200, verbose_name='反馈')
    sign_company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='fso_tail_company', null=True,
                                     blank=True, verbose_name='创建公司')
    sign_department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE, related_name='fso_tail_department',
                                        null=True, blank=True, verbose_name='创建部门')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')


    class Meta:
        verbose_name = 'EXT-尾货账单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_final'

    def __str__(self):
        return str(self.order_id)


# 应收结算单待结算
class FSAffirm(FinalStatement):
    class Meta:
        verbose_name = 'EXT-尾货账单-重损待确认'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单待结算
class FSSpecialAffirm(FinalStatement):
    class Meta:
        verbose_name = 'EXT-尾货账单-非重损待确认'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单待结算
class FSSubmit(FinalStatement):
    class Meta:
        verbose_name = 'EXT-尾货账单-待支付'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单待结算
class FSCheck(FinalStatement):
    class Meta:
        verbose_name = 'EXT-尾货账单-重损待结算'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单待结算
class FSSpecialCheck(FinalStatement):
    class Meta:
        verbose_name = 'EXT-尾货账单-非重损待结算'
        verbose_name_plural = verbose_name
        proxy = True


# 最终付款结算单货品明细
class FinalStatementGoods(BaseModel):
    CATEGORY = (
        (1, '销售订单'),
        (2, '售后换货'),
        (3, '退-退货退款'),
        (4, '退-换货退回'),
        (5, '退-仅退款'),
    )
    fs_order = models.ForeignKey(FinalStatement, on_delete=models.CASCADE, verbose_name='结算单号')
    order_category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='结算类型')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='数量')
    settlement_price = models.FloatField(verbose_name='含税单价')
    settlement_amount = models.FloatField(verbose_name='货品总价')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')

    class Meta:
        verbose_name = 'EXT-尾货账单-货品明细'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_final_goods'

    def __str__(self):
        return str(self.fs_order.order_id)


# 结算明细单
class AccountInfo(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '待生成'),
        (2, '待支付'),
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
        (1, '汇总出错，重新汇总'),
        (2, '汇总货品出错，联系管理员'),
        (3, '已登记过账单，联系管理员'),

    )
    CATEGORY = (
        (1, '销售订单'),
        (2, '售后换货'),
        (3, '退-退货退款'),
        (4, '退-换货退回'),
        (5, '退-仅退款'),
    )
    MODE_W = (
        (0, '回流'),
        (1, '二手'),
    )

    order_id = models.CharField(unique=True, max_length=100, verbose_name='账单单号', db_index=True)
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    mode_warehouse = models.SmallIntegerField(choices=MODE_W, null=True, blank=True, verbose_name='发货模式')
    order_category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='结算类型')
    goods_id = models.CharField(max_length=50, verbose_name='货品编码', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, verbose_name='货品名称')
    goods_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='数量')
    settlement_price = models.FloatField(verbose_name='结算货品单价')
    settlement_amount = models.FloatField(verbose_name='结算货品总价')
    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机', db_index=True)

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')

    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='处理间隔(分钟)')

    final_statement = models.ForeignKey(FinalStatement, on_delete=models.CASCADE, null=True, blank=True,
                                        verbose_name='结算单')

    message = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')
    feedback = models.CharField(null=True, blank=True, max_length=200, verbose_name='反馈')
    sign_company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='acc_tail_company', null=True,
                                     blank=True, verbose_name='创建公司')
    sign_department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE, related_name='acc_tail_department',
                                        null=True, blank=True, verbose_name='创建部门')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'EXT-尾货对账明细-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_account'


# 应收结算单待结算
class AccountCheck(AccountInfo):
    class Meta:
        verbose_name = 'EXT-尾货对账明细-重损未处理'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单待结算
class AccountSpecialCheck(AccountInfo):
    class Meta:
        verbose_name = 'EXT-尾货对账明细-非重损未处理'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单待结算
class AccountUnfinished(AccountInfo):
    class Meta:
        verbose_name = 'EXT-尾货对账明细-未完成'
        verbose_name_plural = verbose_name
        proxy = True


class PBillToAccount(BaseModel):
    pbo_order = models.OneToOneField(PBOGoods, on_delete=models.CASCADE, verbose_name='付款单货品明细')
    account_order = models.ForeignKey(AccountInfo, on_delete=models.CASCADE, verbose_name='对账明细单')

    class Meta:
        verbose_name = 'EXT-尾货付款对账对照表'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_p2a'


class ABillToAccount(BaseModel):
    abo_order = models.OneToOneField(ABOGoods, on_delete=models.CASCADE, verbose_name='退款单货品明细')
    account_order = models.ForeignKey(AccountInfo, on_delete=models.CASCADE, verbose_name='对账明细单')

    class Meta:
        verbose_name = 'EXT-尾货退款对账对照表'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_a2a'


class TailPartsOrder(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '未递交'),
        (2, '已生成'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '驳回'),
        (6, '特殊订单'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '货品包含整机'),
        (2, '配件名称错误或未添加'),
        (3, '没收货人'),
        (4, '14天内重复'),
        (5, '14天外重复'),
        (6, '手机号错误'),
        (7, '地址是集运仓'),
        (8, '收货人信息不全'),
        (9, '城市错误'),
        (10, '单据生成出错'),
        (11, '店铺错误'),
        (12, '电话重复'),
        (13, '售后配件需要补全sn、部件和描述'),

    )
    ORDER_CATEGORY = (
        (1, '质量问题'),
        (2, '开箱即损'),
        (3, '礼品赠品'),
    )

    order_id = models.CharField(max_length=150, null=True, blank=True, verbose_name='配件单号')
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机')
    sent_city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='收件城市')
    sent_district = models.CharField(null=True, blank=True, max_length=30, verbose_name='收件区县')
    sent_address = models.CharField(max_length=200, verbose_name='收件地址')
    sign_company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='tailpart_company',
                                     null=True, blank=True, verbose_name='创建公司')
    sign_department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE, related_name='tailpart_department',
                                        null=True, blank=True, verbose_name='创建部门')
    parts_info = models.CharField(max_length=300, null=True, blank=True, verbose_name='配件信息')
    message = models.TextField(null=True, blank=True, verbose_name='备注')

    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='订单状态')
    order_category = models.SmallIntegerField(choices=ORDER_CATEGORY, default=3, verbose_name='单据类型')

    m_sn = models.CharField(null=True, blank=True, max_length=50, verbose_name='机器序列号')
    broken_part = models.CharField(null=True, blank=True, max_length=50, verbose_name='故障部位')
    description = models.CharField(null=True, blank=True, max_length=200, verbose_name='故障描述')

    class Meta:
        verbose_name = 'EXT-尾货配件-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_tailorder_part'

    def __str__(self):
        return str(self.order_id)


# 应收结算单待结算
class SubmitTPO(TailPartsOrder):
    class Meta:
        verbose_name = 'EXT-尾货配件-未提交'
        verbose_name_plural = verbose_name
        proxy = True