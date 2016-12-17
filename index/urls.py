# -*- coding:utf-8 -*-

from django.conf.urls import include, url
from index.views import ( dashboard,
                        Stock,
                        add_cartridge_name,
                        add_cartridge_item,
                        add_cartridge_from_barcode_scanner,
                        add_empty_cartridge_from_barcode_scanner,
                        add_empty_cartridge,
                        tree_list,
                        add_type,
                        transfe_for_use,
                        transfer_to_firm,
                        transfer_to_firm_with_scanner,
                        Use,
                        Empty,
                        toner_refill,
                        add_firm,
                        edit_firm,
                        At_work,
                        bad_browser,
                        Basket,
                        edit_cartridge_comment,
                        from_firm_to_stock,
                        from_firm_to_stock_with_barcode,
                        evaluate_service,
                        Bufer,
                        worked_firms,
                        )

urlpatterns = [
    url(r'^$', dashboard, name='dashboard'),
    url(r'^api/', include('index.api.urls')),
    url(r'^stock/', Stock.as_view(), name='stock'),
    url(r'^add_name/', add_cartridge_name, name='add_name'),
    url(r'^add_items/', add_cartridge_item, name='add_items'),
    url(r'^add_cartridge_from_barcode_scanner/', add_cartridge_from_barcode_scanner, name='add_cartridge_from_barcode_scanner'),
    url(r'^add_empty_cartridge_from_barcode_scanner/', add_empty_cartridge_from_barcode_scanner, name='add_empty_cartridge_from_barcode_scanner'),
    url(r'^add_empty_cartridge/', add_empty_cartridge, name='add_empty_cartridge'),
    url(r'^tree_list/', tree_list, name='tree_list'),
    url(r'^add_type/', add_type, name='add_type'),
    url(r'^transfe_for_use/', transfe_for_use, name='transfe_for_use'),
    url(r'^transfer_to_firm/', transfer_to_firm, name='transfer_to_firm'),
    url(r'^transfer_to_firm_with_scanner/', transfer_to_firm_with_scanner, name='transfer_to_firm_with_scanner'),
    url(r'^at_work/(?P<pk>\d+)/$', At_work.as_view(), name='at_work'),
    url(r'^use/', Use.as_view(), name='use'),
    url(r'^empty/', Empty.as_view(), name='empty'),
    url(r'^toner_refill/', toner_refill, name='toner_refill'),
    url(r'^add_firm/', add_firm, name='add_firm'),
    url(r'^edit_firm/', edit_firm, name='edit_firm'),
    url(r'^bad_browser/', bad_browser, name='bad_browser'),
    url(r'^basket/', Basket.as_view(), name='basket'),
    url(r'^edit_cartridge_comment/', edit_cartridge_comment, name='edit_cartridge_comment'),
    url(r'^from_firm_to_stock/', from_firm_to_stock, name='from_firm_to_stock'),
    url(r'^from_firm_to_stock_with_barcode/', from_firm_to_stock_with_barcode, name='from_firm_to_stock_with_barcode'),
    url(r'^evaluate_service/', evaluate_service, name='evaluate_service'),
    url(r'^bufer/', Bufer.as_view(), name='bufer'),
    url(r'^worked_firms/', worked_firms, name='worked_firms'),
]
