# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 20:58
# @Author  : Hann
# @Site    :
# @File    : xadmin.py.py
# @Software: PyCharm

import re
import xadmin
import pandas as pd

from .models import GoodsInfo, PartInfo, MachineInfo


class GoodsInfoAdmin(object):
    list_display = ['goods_name', 'goods_id', 'goods_attribute', 'goods_number']
    list_filter = ['goods_name', 'goods_id', 'goods_attribute',]
    search_fields = ['goods_name']
    relfield_style = 'fk-ajax'



class MachineInfoAdmin(object):
    list_display = ['goods_name', 'goods_id', 'goods_attribute', 'goods_number']
    list_filter = ['goods_name', 'goods_id', 'goods_attribute',]
    search_fields = ['goods_id', 'goods_name']
    # 设置这个外键用搜索的方式输入
    relfield_style = 'fk-ajax'

    def queryset(self):
        qs = super(MachineInfoAdmin, self).queryset()
        qs = qs.filter(goods_attribute=0)
        return qs


class PartInfoAdmin(object):
    list_display = ['goods_name']
    list_filter = ['goods_name', 'goods_id', 'goods_attribute',]
    search_fields = ['goods_name']
    relfield_style = 'fk-ajax'
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {
        '商家编码': 'goods_id',
        '简称': 'goods_name',
    }
    import_data = True

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('导入成功数据%s条' % int(result['successful']), 'success')
            if result['false'] > 0 or result['error']:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (int(result['false']), result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('包含更新重复数据%s条' % int(result['repeated']), 'error')
        return super(PartInfoAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype={"商家编码": str})

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = PartInfo.verify_mandatory(columns_key)
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
                _ret_verify_field = PartInfo.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return report_dic['error'].append(_ret_verify_field)
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
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        # 开始导入数据
        for row in resource:
            if not re.match(r'^[0-9]*$', str(row['goods_id'])):
                report_dic['discard'] += 1
                continue
            _q_goods_order = PartInfo.objects.filter(goods_id=row['goods_id'])
            if _q_goods_order.exists():
                goods_order = _q_goods_order[0]
                if row['goods_name'] == goods_order.goods_name:
                    continue
                else:
                    goods_order.goods_name = row['goods_name']
            else:
                goods_order = GoodsInfo()
                goods_order.goods_id = row['goods_id']
                goods_order.goods_attribute = 1
                goods_order.goods_number = row['goods_id']
                goods_order.goods_name = row['goods_name']

            try:
                goods_order.creator = request.user.username
                goods_order.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["false"] += 1
                report_dic["error"].append(e)
        return report_dic

    def queryset(self):
        qs = super(PartInfoAdmin, self).queryset()
        qs = qs.filter(goods_attribute=1)
        return qs


xadmin.site.register(MachineInfo, MachineInfoAdmin)
xadmin.site.register(PartInfo, PartInfoAdmin)
xadmin.site.register(GoodsInfo, GoodsInfoAdmin)

