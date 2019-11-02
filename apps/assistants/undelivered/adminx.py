# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 9:19
# @Author  : Hann
# @Site    :
# @File    : adminx.py.py
# @Software: PyCharm


from django.core.exceptions import PermissionDenied
import pandas as pd
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext


from .models import OriorderInfo, PendingOrderInfo, SpecialOrderInfo, RefundOrderInfo


class ModifyAction(BaseActionView):
    action_name = "update_selected"
    description = '审核对应项目为暂不处理'

    delete_confirmation_template = None
    delete_selected_confirmation_template = None

    modify_models_batch = True

    model_perm = 'change'
    icon = 'fa fa-flag'

    @filter_hook
    def do_action(self, queryset):
        # Check that the user has change permission for the actual model
        if not self.has_change_permission():
            raise PermissionDenied

        n = queryset.count()
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量修改了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(status=3)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.update(status=3)
            self.message_user("成功审核 %(count)d %(items)s." % {
                "count": n, "items": model_ngettext(self.opts, n)
            }, 'success')
        # Return None to display the change list page again.
        return None


class OriorderInfoAdmin(object):

    list_display = ['order_id', 'nickname', 'total_amount', 'payment_amount', 'order_status', 'payment_time', 'goods_title',
                    'goods_quantity', 'shop_name', 'refund_amount','create_time', 'creator', 'status']
    list_filter = ['payment_time', 'shop_name', 'status']
    search_fields = ["order_id", "nickname"]
    # model_icon = 'fa fa-refresh'
    ordering = ['payment_time']
    exclude = ['creator']


class PendingOrderInfoAdmin(object):
    INIT_FIELDS_DIC = {
        '订单编号': 'order_id',
        '买家会员名': 'nickname',
        '买家支付宝账号': 'alipay_id',
        '支付单号': 'alipay_order_id',
        '支付详情': 'alipay_desc',
        '买家应付货款': 'account_payable',
        '买家应付邮费': 'post_fee',
        '买家支付积分': 'point_payable',
        '总金额': 'total_amount',
        '返点积分': 'point',
        '买家实际支付金额': 'payment_amount',
        '买家实际支付积分': 'payment_point',
        '订单状态': 'order_status',
        '买家留言': 'buyer_message',
        '收货人姓名': 'receiver',
        '收货地址': 'address',
        '运送方式': 'delivery_type',
        '联系电话': 'telephone',
        '联系手机': 'mobile',
        '订单创建时间': 'order_create_time',
        '订单付款时间': 'payment_time',
        '宝贝标题': 'goods_title',
        '宝贝种类': 'goods_type',
        '订单备注': 'memorandum',
        '宝贝总数量': 'goods_quantity',
        '店铺Id': 'shop_id',
        '店铺名称': 'shop_name',
        '订单关闭原因': 'cause_closed',
        '退款金额': 'refund_amount',
    }
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    list_display = ['goods_title', 'status', 'order_id', 'nickname', 'total_amount', 'payment_amount', 'memorandum',
                    'order_status', 'payment_time', 'goods_quantity', 'shop_name', 'refund_amount', 'create_time',
                    'creator']
    list_filter = ['payment_time', 'shop_name', 'goods_title', 'payment_amount', 'refund_amount']
    search_fields = ["order_id", "nickname"]
    # model_icon = 'fa fa-refresh'
    list_editable = ['status', 'memorandum']
    ordering = ['payment_time']
    exclude = ['creator']
    actions = [ModifyAction, ]
    import_data = True

    def post(self, request, *args, **kwargs):
        creator = request.user.username
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(file, creator)
            self.message_user('导入成功数据%s条' % result['successful'], 'success')
            if result['false'] > 0:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (result['false'],result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('包含更新重复数据%s条' % result['repeated'], 'error')
        return super(PendingOrderInfoAdmin, self).post(request, args, kwargs)

    def handle_upload_file(self, _file, creator):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            with pd.ExcelFile(_file) as xls:
                df = pd.read_excel(xls, sheet_name=0)

                # 获取表头，对表头进行转换成数据库字段名
                columns_key = df.columns.values.tolist()
                for i in range(len(columns_key)):
                    columns_key[i] = columns_key[i].replace(' ', '').replace('=', '')

                for i in range(len(columns_key)):
                    if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

                # 验证一下必要的核心字段是否存在
                _ret_verify_field = OriorderInfo.verify_mandatory(columns_key)
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
                    intermediate_report_dic = self.save_resources(_ret_list, creator)
                    for k, v in intermediate_report_dic.items():
                        if k == "error":
                            if intermediate_report_dic["error"]:
                                report_dic[k].append(v)
                        else:
                            report_dic[k] += v
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
                _ret_verify_field = OriorderInfo.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field
                # 验证通过进行重新处理。
                columns_key_ori = piece.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                piece.rename(columns=ret_columns_key, inplace=True)
                _ret_list = piece.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(_ret_list, creator)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
            return report_dic

        else:
            return "只支持excel和csv文件格式！"

    def save_resources(self, resource, creator):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        # 开始导入数据
        for row in resource:
            # ERP导出文档添加了等于号，毙掉等于号。
            order = OriorderInfo()  # 创建表格每一行为一个对象
            # 清除订单号的特殊字符
            row['order_id'] = str(row['order_id']).replace("=", "").replace('"', "")
            row['alipay_orer_id'] = str(row['alipay_order_id']).replace("=", "").replace('"', "")
            row['mobile'] = str(row['mobile']).replace("'", "")
            reservation_keywords = ['定金', '预', '订金', '券']
            order_id = row['order_id']

            # 如果订单号查询，已经存在，丢弃订单，计数为重复订单
            target_order = OriorderInfo.objects.all().filter(order_id=order_id)
            if target_order.exists():
                if row['order_status'] == '买家已付款，等待卖家发货' and target_order[0].status not in [1, 2, 4, 5]:
                    target_order[0].status = 0
                    if row['refund_amount'] > 0:
                        target_order[0].status = 4
                    try:
                        target_order[0].save()
                        report_dic["successful"] += 1
                    # 保存出错，直接错误条数计数加一。
                    except Exception as e:
                        report_dic["error"].append(e)
                        report_dic["false"] += 1
                report_dic["repeated"] += 1
                continue
            for k, v in row.items():
                # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
                if hasattr(order, k):
                    if str(v) in ['nan', 'NaT']:
                        pass
                    else:
                        setattr(order, k, v)  # 更新对象属性为字典对应键值
            # 对订单进行分类判断
            order.status = 0
            if order.total_amount < 10.1:
                order.status = 5
            if any(keyword in order.goods_title for keyword in reservation_keywords):
                order.status = 5
            if order.refund_amount > 0:
                order.status = 4

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
        qs = OriorderInfo.objects.all().filter(status=0)
        return qs

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class SpecialOrderInfoAdmin(object):
    list_display = ['goods_title', 'status', 'order_id', 'nickname', 'total_amount', 'payment_amount', 'memorandum',
                    'order_status', 'payment_time', 'goods_quantity', 'shop_name', 'refund_amount', 'create_time',
                    'creator']
    list_filter = ['payment_time', 'shop_name', 'status']
    list_editable = ['status', 'memorandum']
    ordering = ['payment_time']
    exclude = ['creator']

    def queryset(self):
        qs = OriorderInfo.objects.all().filter(status=2)
        return qs

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class RefundOrderInfoAdmin(object):
    list_display = ['goods_title', 'status', 'order_id', 'nickname', 'total_amount', 'payment_amount', 'memorandum',
                    'order_status', 'payment_time', 'goods_quantity', 'shop_name', 'refund_amount', 'create_time',
                    'creator']
    list_filter = ['create_time', 'payment_time', 'shop_name', 'status']
    list_editable = ['status', 'memorandum']
    ordering = ['payment_time']
    exclude = ['creator']

    def queryset(self):
        qs = OriorderInfo.objects.all().filter(status=4)
        return qs

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(PendingOrderInfo, PendingOrderInfoAdmin)
xadmin.site.register(SpecialOrderInfo, SpecialOrderInfoAdmin)
xadmin.site.register(RefundOrderInfo, RefundOrderInfoAdmin)
xadmin.site.register(OriorderInfo, OriorderInfoAdmin)