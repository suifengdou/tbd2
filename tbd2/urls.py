"""tbd2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
import xadmin

from apps.users.views import IndexView

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^users/', include('apps.users.urls', namespace='users')),
    url(r'^assistants/refund/jdfbp/', include('apps.assistants.refund_jdfbp.urls', namespace='ass_ref_jdfbp')),
    url(r'^external/express/sf/', include('apps.ext.sf_consignation.urls', namespace='ext_exp_sf')),
    # url(r'^crm/orders/', include('apps.crm.orders.urls', namespace='crm_orders')),
    url(r'^crm/maintenance/', include('apps.crm.maintenance.urls', namespace='crm_maintenance')),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^crm/refurbishment/', include('apps.crm.refurbishment.urls', namespace='crm_refurbishment')),
    ]
