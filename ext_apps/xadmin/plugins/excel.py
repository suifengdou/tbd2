# -*- coding: utf-8 -*-
# @Time    : 2019/6/11 8:56
# @Author  : Hann
# @Site    : 
# @File    : importdata.py
# @Software: PyCharm

import xadmin
from xadmin.views import BaseAdminPlugin, ListAdminView
from django.template import loader
from xadmin.plugins.utils import get_context_dict


# 表格导入模块支持excel和csv
class ListImportDataPlugin(BaseAdminPlugin):
    import_data = False

    def init_request(self, *args, **kwargs):
        return bool(self.import_data)

    def block_top_toolbar(self, context, nodes):
        nodes.append(loader.render_to_string('xadmin/excel/model_list.top_toolbar.import.html', context=get_context_dict(context)))




xadmin.site.register_plugin(ListImportDataPlugin, ListAdminView)