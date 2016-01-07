# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse

def show_events(request):
    """Список событий для заданного картриджа.

        номер события \ номер картриджа \ дата \ текст человекочитаемого события \
        Добавлен пользователем "Вася пупкин"
        передан в пользование "ООО Ямал Каб. 290"
        возвращен на склад
        передан на заправку в фирму "Континент"
        возвращен на склад
        перемещён в корзину
    """
    return HttpResponse('<h1>Events it work!</h1>')


def view_cartridge_events(request):
    """Просмотр событий происходящих с данным картриджем.
    """
    return HttpResponse('<h1>Просмотр событий для картриджа работает!</h1>')