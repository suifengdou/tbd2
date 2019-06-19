# -*- coding: utf-8 -*-
# @Time    : 2019/4/10 9:03
# @Author  : Hann
# @Site    : 
# @File    : adminx.py.py
# @Software: PyCharm
import re

from django.core.exceptions import PermissionDenied


from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
import xadmin
import pandas as pd

from .models import RefundResource, PendingRefundResource


class ModifyAction(BaseActionView):
    action_name = "update_selected"
    description = '审核对应项目'

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
                queryset.update(handlingstatus=1)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.update(handlingstatus=1)
            self.message_user("成功审核 %(count)d %(items)s." % {
                "count": n, "items": model_ngettext(self.opts, n)
            }, 'success')
        # Return None to display the change list page again.
        return None


class RefundResourceAdmin(object):
    INIT_FIELDS_DIC = {'服务单号': 'service_order_id', '订单号': 'order_id', '商品编号': 'goods_id', '商品名称': 'goods_name',
                       '商品金额': 'goods_amount', '服务单状态': 'order_status', '售后服务单申请时间': 'application_time',
                       '商家首次审核时间': 'bs_initial_time', '商家首次处理时间': 'bs_handle_time', '售后服务单整体时长': 'duration',
                       '审核结果': 'bs_result', '处理结果描述': 'bs_result_desc', '客户预期处理方式': 'buyer_expectation',
                       '返回方式': 'return_model', '客户问题描述': 'buyer_problem_desc', '最新审核时间': 'last_handle_time',
                       '审核意见': 'handle_opinion', '审核人姓名': 'handler_name', '取件时间': 'take_delivery_time',
                       '取件状态': 'take_delivery_status', '发货时间': 'delivery_time', '运单号': 'express_id',
                       '运费金额': 'express_fee', '快递公司': 'express_company', '商家收货时间': 'receive_time',
                       '收货登记原因': 'refund_reason', '收货人': 'receiver', '处理人': 'completer',
                       '退款金额': 'refund_amount', '换新订单': 'renew_express_id', '换新商品编号': 'renew_goods_id',
                       '是否闪退订单': 'is_quick_refund'}
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    list_display = ['service_order_id', 'order_id', 'goods_id', 'goods_name', 'order_status', 'application_time',
                    'buyer_expectation', 'return_model', 'handler_name', 'express_id', 'express_company', 'handlingstatus']
    search_fields = ['service_order_id', 'order_id', 'express_id']
    list_filter = ['goods_id', 'application_time', 'order_status', 'handlingstatus']
    import_data = True

    def post(self, request, *args, **kwargs):
        creator = request.user.username
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(file, creator)
            self.message_user('导入成功数据%s条' % result['successful'], 'success')
            if result['false'] > 0 or result['error']:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (result['false'], result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('包含更新重复数据%s条' % result['repeated'], 'error')
        return super(RefundResourceAdmin, self).post(request, args, kwargs)

    def handle_upload_file(self, _file, creator):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0)

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = RefundResource.verify_mandatory(columns_key)
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
                intermediate_report_dic = self.save_resources(_ret_list, creator)
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
                _ret_verify_field = RefundResource.verify_mandatory(columns_key)
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
            report_dic["error"].append('只支持excel和csv文件格式！')
            return report_dic

    @staticmethod
    def save_resources(resource, creator):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}

        # 开始导入数据
        for row in resource:
            service_order = RefundResource()  # 创建表格每一行为一个对象
            express_id = str(row["express_id"])
            service_order_id = str(row["service_order_id"])

            # 如果服务单号为空，就丢弃这个订单，计数为丢弃订单
            if re.match(r'^[0-9]', service_order_id) is None:
                report_dic["discard"] += 1
                continue

            # 如果服务单号已经存在，丢弃订单，计数为重复订单
            elif RefundResource.objects.filter(service_order_id=service_order_id).exists():
                report_dic["repeated"] += 1
                continue

            # 如果快递单号为空，则丢弃
            elif re.match(r'^[0-9JVW]', express_id) is None:
                report_dic["discard"] += 1
                continue

            else:
                for k, v in row.items():

                    # 查询是否有这个字段属性，如果有就更新到对象。nan, NaT 是pandas处理数据时候生成的。
                    if hasattr(service_order, k):
                        if str(v) in ['nan', 'NaT']:
                            pass
                        else:
                            setattr(service_order, k, v)  # 更新对象属性为字典对应键值
                try:
                    service_order.creator = creator
                    service_order.handling_status = 0  # 设置默认的操作状态。
                    service_order.save()
                    report_dic["successful"] += 1
                # 保存出错，直接错误条数计数加一。
                except Exception as e:
                    report_dic["false"] += 1
                    report_dic["error"].append(e)
        return report_dic


class PendingRefundResourceAdmin(object):
    list_display = ['goods_name', 'handlingstatus', 'service_order_id', 'order_id', 'express_id', 'express_company',
                    'order_status', 'application_time', 'buyer_expectation', 'return_model']
    search_fields = ['service_order_id', 'order_id', 'express_id']
    list_filter = ['application_time', 'handlingstatus']
    list_editable = ['handlingstatus']
    actions = [ModifyAction, ]

    def queryset(self):
        qs = RefundResource.objects.all().filter(handlingstatus=0)
        return qs

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(RefundResource, RefundResourceAdmin)
xadmin.site.register(PendingRefundResource, PendingRefundResourceAdmin)