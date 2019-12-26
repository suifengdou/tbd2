# -*- coding: utf-8 -*-
# @Time    : 2019/11/18 9:21
# @Author  : Hann
# @Site    : 
# @File    : batchfilter.py
# @Software: PyCharm


import xadmin
from xadmin.views import BaseAdminPlugin, ListAdminView
from django.template import loader
from xadmin.plugins.utils import get_context_dict


class ListBatchFilterPlugin(BaseAdminPlugin):
    batch_data = False

    def init_request(self, *args, **kwargs):
        return bool(self.batch_data)

    def block_top_toolbar(self, context, nodes):
        nodes.append(loader.render_to_string('xadmin/batchfilter/batch_filter.html', context=get_context_dict(context)))


xadmin.site.register_plugin(ListBatchFilterPlugin, ListAdminView)

