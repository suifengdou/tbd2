# -*- coding: utf-8 -*-
# @Time    : 2019/10/18 20:29
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm
import re

from django.core.files.uploadedfile import InMemoryUploadedFile

import xadmin


from .models import GiftInTalkPendding, GiftInTalkInfo, GiftOrderPendding, GiftOrderInfo


class GiftInTalkPenddingAdmin(object):
    list_display = ['receiver', 'mobile', 'address', 'goods_name', 'quantity', 'servicer', 'nickname', 'order_id', 'order_status']

    ALLOWED_EXTENSIONS = ['log',]
    INIT_FIELDS_DIC = {"源单号": "express_id", "初始问题信息": "information", "工单事项类型": "category"}
    import_data = True

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            # result = self.handle_upload_file(request, file)
            file_to_read = file.chunks(chunk_size=3)
            text_list = []

            for i in file_to_read:
                print(i)
                s = i.decode("utf-8")
                text_list.append(i)

            print(text_list)
            file_to_read.close()
            self.message_user('导入成功数据%s条' % int(result['successful']), 'success')
            if result['false'] > 0 or result['error']:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (int(result['false']), result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('包含更新重复数据%s条' % int(result['repeated']), 'error')
        return super(GiftInTalkPenddingAdmin, self).post(request, args, kwargs)

    # def handle_upload_file(self, request, _file):
    #     report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
    #     if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
    #         with open(_file, 'r', encoding="utf-8") as file_to_read:
    #             report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}
    #             category_dic = {'截单退回': 0, '无人收货': 1, '客户拒签': 2, '修改地址': 3, '催件派送': 4, '虚假签收': 5, '其他异常': 6}
    #             while True:
    #                 lines = file_to_read.readline()
    #                 if not lines:
    #                     break
    #                 elif "·客服" in lines:
    #                     result = re.findall("{.*}?", lines)
    #                     print(result)
    #
    #         print(report_dic)
    #
    #         return report_dic

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.save()
        super().save_models()

xadmin.site.register(GiftInTalkPendding, GiftInTalkPenddingAdmin)