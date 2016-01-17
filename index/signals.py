# -*- config:utf-8 -*-

from django.apps import AppConfig
from django.dispatch import Signal
from django.utils import timezone
from .models import CartridgeItem
from events.models import Events

sign_add_full_to_stock       = Signal(providing_args=['num', 'cart_type', 'user', 'request'])
sign_tr_cart_to_uses         = Signal(providing_args=['list_cplx', 'org' , 'request'])
sign_tr_cart_to_basket       = Signal(providing_args=['list_cplx', 'request'])
sign_tr_empty_cart_to_stock  = Signal(providing_args=['list_cplx', 'request'])
sign_turf_cart               = Signal(providing_args=['list_cplx', 'request'])
sign_tr_empty_cart_to_firm   = Signal(providing_args=['list_cplx', 'request','firm'])
sign_tr_filled_cart_to_stock = Signal(providing_args=['list_cplx', 'request'])

def event_add_cart(**kwargs):
    m1 = Events(departament = kwargs.get('request').user.departament.pk,
                date_time   = timezone.now(),
                cart_number = kwargs.get('num', 0),
                cart_type   = kwargs.get('cart_type', 0),
                event_type  = 'AD',
                event_user  = kwargs.get('user', 'anonymous'),
                )
    m1.save()


def event_transfe_cart_to_uses(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Ошибка в обработчике event_transfe_cart_to_uses!')
    
    for elem in kwargs.get('list_cplx'):
        m1 = Events(departament = kwargs.get('request').user.departament.pk,
            date_time   = timezone.now(),
            cart_number = elem[0],
            cart_type   = elem[1],
            event_type  = 'TR',
            event_user  = str(kwargs.get('request').user),
            event_org   = kwargs.get('org')
        )
        m1.save()

def event_transfe_cart_to_basket(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Ошибка в обработчике event_transfe_cart_to_basket!')
    
    for elem in kwargs.get('list_cplx'):
        m1 = Events(departament = kwargs.get('request').user.departament.pk,
            date_time   = timezone.now(),
            cart_number = elem[0],
            cart_type   = elem[1],
            event_type  = 'TB',
            event_user  = str(kwargs.get('request').user),
        )
        m1.save()


def event_tr_empty_cart_to_stock(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Ошибка в обработчике event_tr_empty_cart_to_stock!')

    for elem in kwargs.get('list_cplx'):
        m1 = Events(departament = kwargs.get('request').user.departament.pk,
            date_time   = timezone.now(),
            cart_number = elem[0],
            cart_type   = elem[1],
            event_type  = 'TS',
            event_user  = str(kwargs.get('request').user),
        )
        m1.save()


def event_turf_cart(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Ошибка в обработчике event_turf_cart!')

    for elem in kwargs.get('list_cplx'):
        m1 = Events(departament = kwargs.get('request').user.departament.pk,
            date_time   = timezone.now(),
            cart_number = elem[0],
            cart_type   = elem[1],
            event_type  = 'DC',
            event_user  = str(kwargs.get('request').user),
        )
        m1.save()

def event_tr_empty_cart_to_firm(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Ошибка в обработчике event_tr_empty_cart_to_firm!')

    for elem in kwargs.get('list_cplx'):
        m1 = Events(departament = kwargs.get('request').user.departament.pk,
            date_time   = timezone.now(),
            cart_number = elem[0],
            cart_type   = elem[1],
            event_type  = 'TF',
            event_firm  = kwargs.get('firm'),
            event_user  = str(kwargs.get('request').user),
        )
        m1.save()


def event_tr_filled_cart_to_stock(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Ошибка в обработчике event_tr_filled_cart_to_stock!')

    for elem in kwargs.get('list_cplx'):
        m1 = Events(departament = kwargs.get('request').user.departament.pk,
            date_time   = timezone.now(),
            cart_number = elem[0],
            cart_type   = elem[1],
            event_type  = 'RS',
            event_firm  = elem[2],
            event_user  = str(kwargs.get('request').user),
        )
        m1.save()

sign_add_full_to_stock.connect(event_add_cart)
sign_tr_cart_to_uses.connect(event_transfe_cart_to_uses)
sign_tr_cart_to_basket.connect(event_transfe_cart_to_basket)
sign_tr_empty_cart_to_stock.connect(event_tr_empty_cart_to_stock)
sign_turf_cart.connect(event_turf_cart)
sign_tr_empty_cart_to_firm.connect(event_tr_empty_cart_to_firm)
sign_tr_filled_cart_to_stock.connect(event_tr_filled_cart_to_stock)