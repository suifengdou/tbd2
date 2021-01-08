from django.db import models

# Create your models here.

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.utils.geography.models import CityInfo, ProvinceInfo, DistrictInfo
from apps.base.company.models import MainInfo, CompanyInfo
from apps.base.shop.models import ShopInfo
from apps.base.department.models import DepartmentInfo


class WorkOrderDealerPart(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '未递交'),
        (2, '未审核'),
        (3, '已生成'),
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
        (1, '一个订单不可重复递交'),
        (2, '同一收件人有多个订单'),
        (3, '货品名称包含整机不是配件'),
        (4, '货品名称错误，或者货品格式错误'),
        (5, '店铺错误'),
        (6, '手机号错误'),
        (7, '地址是集运仓'),
        (8, '收货人信息不全'),
        (9, '14天内重复递交过订单'),
        (10, '14天外重复递交过订单'),
        (11, '创建配件发货单错误'),
        (12, '无三级区县'),
        (13, '售后配件需要补全sn、部件和描述'),
    )
    ORDER_CATEGORY = (
        (1, '质量问题'),
        (2, '开箱即损'),
        (3, '礼品赠品'),
    )

    order_id = models.CharField(max_length=150, verbose_name='源订单号')
    shop = models.ForeignKey(ShopInfo, on_delete=models.CASCADE, verbose_name='店铺')
    nickname = models.CharField(max_length=150, verbose_name='客户网名')
    sent_consignee = models.CharField(max_length=150, verbose_name='收件人姓名')
    sent_smartphone = models.CharField(max_length=30, verbose_name='收件人手机')
    sent_city = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='收件城市')
    sent_district = models.CharField(null=True, blank=True, max_length=30, verbose_name='收件区县')
    sent_address = models.CharField(max_length=200, verbose_name='收件地址')
    sign_company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='wodp_company',
                                     null=True, blank=True, verbose_name='创建公司')
    sign_department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE, related_name='wodp_department',
                                        null=True, blank=True, verbose_name='创建部门')
    parts_info = models.CharField(max_length=300, verbose_name='配件信息')
    message = models.TextField(null=True, blank=True, verbose_name='备注')

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    handler = models.CharField(null=True, blank=True, max_length=150, verbose_name='处理人')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    handle_interval = models.IntegerField(null=True, blank=True, verbose_name='处理间隔(分钟)')

    feedback = models.TextField(null=True, blank=True, verbose_name='订单反馈')

    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='订单状态')
    order_category = models.SmallIntegerField(choices=ORDER_CATEGORY, default=3, verbose_name='单据类型')

    m_sn = models.CharField(null=True, blank=True, max_length=50, verbose_name='机器序列号')
    broken_part = models.CharField(null=True, blank=True, max_length=50, verbose_name='故障部位')
    description = models.CharField(null=True, blank=True, max_length=200, verbose_name='故障描述')

    class Meta:
        verbose_name = 'EXT-经销商配件-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_wo_dealerpart'

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ['order_id', 'shop', 'nickname', 'sent_consignee', 'sent_smartphone', 'sent_city',
                        'sent_district', 'sent_address', 'parts_info', 'message']
        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None

    def __str__(self):
        return str(self.order_id)


# 应收结算单待结算
class SubmitWODP(WorkOrderDealerPart):
    class Meta:
        verbose_name = 'EXT-经销商配件-未提交'
        verbose_name_plural = verbose_name
        proxy = True


# 应收结算单待结算
class CheckWODP(WorkOrderDealerPart):
    class Meta:
        verbose_name = 'EXT-经销商配件-未审核'
        verbose_name_plural = verbose_name
        proxy = True