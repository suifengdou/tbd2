# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 11:22
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


from .models import GoodsToManufactoryInfo, PartToProductInfo, CusPartToManufactoryInfo, MachineToManufactoryInfo, PartToManufactoryInfo, ManufactoryToWarehouse
from apps.base.goods.models import GoodsInfo
from apps.base.company.models import CompanyInfo

class MachineToManufactoryInfoAdmin(object):
    list_display = ["goods_name", "manufactory", "status", "category"]
    search_fields = ["goods_name__goods_name"]
    list_filter = ["manufactory"]

    def queryset(self):
        queryset = super(MachineToManufactoryInfoAdmin, self).queryset()
        queryset = queryset.filter(category=0)
        return queryset


class CusPartToManufactoryInfoAdmin(object):
    list_display = ["goods_name", "manufactory", "status", "category"]

    def queryset(self):
        queryset = super(CusPartToManufactoryInfoAdmin, self).queryset()
        queryset = queryset.filter(category=1)
        return queryset


class PartToManufactoryInfoAdmin(object):
    list_display = ["goods_name", "manufactory", "status", "category"]

    def queryset(self):
        queryset = super(PartToManufactoryInfoAdmin, self).queryset()
        queryset = queryset.filter(category=2)
        return queryset


class GoodsToManufactoryInfoAdmin(object):
    list_display = ["goods_name", "manufactory", "status", "category"]
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {
        '商家编码': 'goods_id',
        '工厂名字': 'manufactory',
    }
    import_data = True

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('导入结果%s' % result, 'info')

        return super(GoodsToManufactoryInfoAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0)

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = GoodsToManufactoryInfo.verify_mandatory(columns_key)
            if _ret_verify_field is not None:
                return report_dic['error'].append(_ret_verify_field)

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
                intermediate_report_dic = self.save_resources(request, _ret_list)
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
            df = pd.read_csv(_file, encoding="GBK", chunksize=900)

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
                _ret_verify_field = GoodsToManufactoryInfo.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field
                # 验证通过进行重新处理。
                columns_key_ori = piece.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                piece.rename(columns=ret_columns_key, inplace=True)
                _ret_list = piece.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(request, _ret_list)
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
    def save_resources(request, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}

        # 开始导入数据
        for row in resource:
            rela_gtm = GoodsToManufactoryInfo()
            check_goods = GoodsInfo.objects.filter(is_delete=0, goods_id=row['goods_id'])
            if check_goods.exists():
                check_goods = check_goods[0]
                if check_goods.goods_attribute == 0:
                    rela_gtm.category = 0
                else:
                    rela_gtm.category = 1
                rela_gtm.goods_name = check_goods
            else:
                report_dic['error'].append("%s 货品编码错误" % row['goods_id'])
                report_dic['false'] += 1
                continue

            check_manu = CompanyInfo.objects.filter(is_delete=0, category=3, company_name=row["manufactory"])
            if check_manu.exists():
                rela_gtm.manufactory = check_manu[0]
            else:
                report_dic['error'].append("%s 工厂错误" % row['manufactory'])
                report_dic['false'] += 1
                continue

            try:
                rela_gtm.creator = request.user.username
                rela_gtm.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["false"] += 1
                report_dic["error"].append(e)
        return report_dic



class PartToProductInfoAdmin(object):
    list_display = ["machine_name", "part_name", "magnification", "status"]


class ManufactoryToWarehouseAdmin(object):
    list_display = ["manufactory", "warehouse", "status"]
    list_filter = ['status']
    search_fields = ['manufactory']


xadmin.site.register(ManufactoryToWarehouse, ManufactoryToWarehouseAdmin)
xadmin.site.register(MachineToManufactoryInfo, MachineToManufactoryInfoAdmin)
xadmin.site.register(CusPartToManufactoryInfo, CusPartToManufactoryInfoAdmin)
xadmin.site.register(PartToManufactoryInfo, PartToManufactoryInfoAdmin)
xadmin.site.register(GoodsToManufactoryInfo, GoodsToManufactoryInfoAdmin)
xadmin.site.register(PartToProductInfo, PartToProductInfoAdmin)
