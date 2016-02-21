# -*- coding:utf-8 -*-

import json
from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from common.helpers import is_admin
from common.cbv import CartridgesView
from common.helpers import BreadcrumbsPath
from .forms.add_cartridge_name import AddCartridgeName
from .forms.add_items import AddItems
from .forms.add_city import CityF
from .forms.add_type import AddCartridgeType
from .forms.add_firm import FirmTonerRefillF
from .forms.comment import EditCommentForm
from .models import CartridgeType
from accounts.models import AnconUser
from django.contrib.auth.models import User
from .models import CartridgeItem
from .models import OrganizationUnits
from .models import City as CityM
from .models import FirmTonerRefill
from .models import CartridgeItemName
from events.models import Events
from events.helpers import events_decoder
from .helpers import recursiveChildren, check_ajax_auth
from .signals import ( sign_tr_cart_to_uses, 
                       sign_tr_cart_to_basket,
                       sign_tr_empty_cart_to_firm,
                       sign_tr_filled_cart_to_stock )

import logging
logger = logging.getLogger('simp')

@login_required
def dashboard(request):
    """Морда сайта. Отображает текущее состояние всего, что считаем.
    """
    try:
        root_ou   = request.user.departament
        children  = root_ou.get_children()
    except AttributeError:
        children = ''
    filter_itms = lambda qy: CartridgeItem.objects.filter(qy)
    context = {}
    context['full_on_stock']  = filter_itms(Q(departament=root_ou) & Q(cart_status=1)).count()
    context['uses']           = filter_itms(Q(departament__in=children) & Q(cart_status=2)).count()
    context['empty_on_stock'] = filter_itms(Q(departament=root_ou) & Q(cart_status=3)).count()
    context['filled']         = filter_itms(Q(departament=root_ou) & Q(cart_status=4)).count()
    context['recycler_bin']   = filter_itms(Q(departament=root_ou) & (Q(cart_status=5) | Q(cart_status=6))).count()
    # формирование контекста топовых событий
    try:
        dept_id = request.user.departament.pk
    except AttributeError:
        dept_id = 0
    MAX_EVENTS = 11
    events_list = Events.objects.filter(departament=dept_id).order_by('-pk')[:MAX_EVENTS]
    if events_list.count() >= MAX_EVENTS:
        context['show_more'] = True
    else:
        context['show_more'] = False
    context['events_list'] = events_decoder(events_list, simple=False)

    # формирование статистики
    import datetime
    cur_date  = timezone.now()
    use_day   = Events.objects.filter(departament=dept_id)
    use_day   = use_day.filter(event_type='TR')
    use_day   = use_day.filter(date_time__year=cur_date.year, date_time__month=cur_date.month, date_time__day=cur_date.day).count()
    
    bld_date  = datetime.datetime(cur_date.year, cur_date.month, 1)
    use_month = Events.objects.filter(departament=dept_id)
    use_month = use_month.filter(event_type='TR')
    use_month = use_month.filter(date_time__gte=bld_date).count()

    bld_date  = datetime.datetime(cur_date.year, 1, 1)
    use_year  = Events.objects.filter(departament=dept_id)
    use_year  = use_year.filter(event_type='TR')
    use_year  = use_year.filter(date_time__gte=bld_date).count()    

    context['use_day']   = use_day
    context['use_month'] = use_month
    context['use_year']  = use_year
    return render(request, 'index/dashboard.html', context)


class Stock(CartridgesView):
    """Списки заправленных, новых картриджей на складе
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Stock, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(Stock, self).get(*args, **kwargs)
        self.context['view'] = 'stock'
        self.all_items = self.all_items.filter(cart_status=1).filter(departament=self.request.user.departament)
        page_size = self.items_per_page()
        self.context['size_perpage'] = page_size
        self.context['cartrjs'] = self.pagination(self.all_items, page_size)
        return render(request, 'index/stock.html', self.context)


@login_required
def add_cartridge_name(request):
    back = BreadcrumbsPath(request).before_page(request)
    if request.method == 'POST':
        form_obj = AddCartridgeName(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            cart_name = data_in_post.get('cart_itm_name','')
            cart_name = cart_name.strip()
            if CartridgeItemName.objects.filter(cart_itm_name__iexact=cart_name):
                # если имя расходника уже занято
                messages.error(request, _('%(cart_name)s already exists') % {'cart_name': cart_name})
            else:    
                # добавляем новый тип расходного материала
                form_obj.save()
                messages.success(request, _('%(cart_name)s success added') % {'cart_name': cart_name})
            return HttpResponseRedirect(request.path)
    else:
        form_obj = AddCartridgeName()
    return render(request, 'index/add_name.html', {'form': form_obj, 'back': back})


@login_required
def add_cartridge_item(request):
    """Обработку данных формы производим в ajax_add_session_items. Здесь 
       отображаем заполненную форму.
    """
    back = BreadcrumbsPath(request).before_page(request)
    from docs.models import SCDoc
    form_obj = AddItems()
    form_obj.fields['doc'].queryset = SCDoc.objects.filter(departament=request.user.departament).filter(doc_type=1)
    session_data = request.session.get('cumulative_list')
    if not session_data:
        # если в сессии нужные данные отсутствуют, то сразу рендерим форму
        return render(request, 'index/add_items.html', {'form': form_obj, 'session': '', 'back': back})    
    
    session_data = json.loads(session_data)
    simple_cache = dict()
    list_names = CartridgeItemName.objects.all()
    for elem in list_names:
        simple_cache[elem.pk] = elem.cart_itm_name
    list_items = list()
    for elem in session_data:
        try:
           title = str(SCDoc.objects.get(pk=elem[1]))
        except SCDoc.DoesNotExist:
            title = ''
        list_items.append({'name': simple_cache.get(elem[0]), 
                           'numbers': str(elem[2])[1:-1], 
                           'title': title})

    html = render_to_string('index/add_over_ajax.html', context={'list_items': list_items})
    return render(request, 'index/add_items.html', {'form': form_obj, 'session': html, 'back': back})


@login_required
@is_admin
def tree_list(request):
    """Работаем с структурой организации
    """
    error1 = ''
    if request.method == 'POST':
        uid = request.POST.get('departament', '')        
        org_name = request.POST.get('name', '') 
        try:
            uid = int(uid)
        except ValueError:
            uid = 0

        # проверям, есть ли такая корневая нода уже в базе
        if uid == 0:
            for node in OrganizationUnits.objects.root_nodes():
                if node == org_name:
                    error1 = _('Organization unit %(org_name)s exist') % {'org_name': org_name}
                    break        
            else:
                # если ноды нет, добавляем
                rock = OrganizationUnits.objects.create(name=org_name)
        
        if uid != 0:
            temp_name = OrganizationUnits.objects.get(pk=uid)
            if temp_name.is_root_node():
                OrganizationUnits.objects.create(name=org_name, parent=temp_name)
            else:    
                for node in temp_name.get_children():
                    if node == org_name:
                        error1 =  _('Organization unit %(org_name)s exist') % {'org_name': org_name}
                        break
                else:
                    rn = OrganizationUnits.objects.get(pk=uid)
                    OrganizationUnits.objects.create(name=org_name, parent=rn)        
            
    bulk = OrganizationUnits.objects.all()
    return render(request, 'index/tree_list.html', {'bulk': bulk, 'error1': error1})


@login_required
def add_type(request):
    """Добавление нового типа расходника, а также редактирование существующего
    """
    back = BreadcrumbsPath(request).before_page(request)
    cart_type_id = request.GET.get('id', '')
    if cart_type_id:
        try:
            cart_type_id = int(cart_type_id)
        except ValueError:
            cart_type_id = 0
        try:
            m1 =  CartridgeType.objects.get(pk=cart_type_id)
        except CartridgeType.DoesNotExist:
            raise Http404
        else:
            form_update = True
    else:
        form_update = False

    if request.method == 'POST':
        
        if form_update: 
            form_obj = AddCartridgeType(request.POST, update=form_update, initial={'cart_type': m1.cart_type, 'comment': m1.comment})
        else:
            form_obj = AddCartridgeType(request.POST, update=form_update)

        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            cart_type = data_in_post['cart_type']
            cart_type_comment = data_in_post['comment']
            if cart_type_id:
                m1.cart_type=cart_type
                m1.comment=cart_type_comment
                m1.save()
                messages.success(request, _('%(cart_type)s success save') % {'cart_type': cart_type})
            else:
                m1 = CartridgeType(cart_type=cart_type, comment=cart_type_comment)
                m1.save()
                messages.success(request, _('New type %(cart_type)s success added') % {'cart_type': cart_type})
            return HttpResponseRedirect(request.path)
        else:
            form = form_obj
    else:
        if cart_type_id:
            form_obj = AddCartridgeType(initial={'cart_type': m1.cart_type, 'comment': m1.comment}, update=form_update)
        else:
            form_obj = AddCartridgeType(update=form_update)
    return render(request, 'index/add_type.html', {'form': form_obj, 'cart_type_id': cart_type_id, 'back': back})


@login_required
def transfe_for_use(request):
    """Передача расходника в пользование.
    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        tmp2 = []
        # преобразовываем айдишники в условные номера
        for cart_id in checked_cartr:
            tmp2.append(CartridgeItem.objects.get(pk=cart_id).cart_number)
        checked_cartr = str(tmp2)
        checked_cartr = checked_cartr[1:-1]
    
    get = lambda node_id: OrganizationUnits.objects.get(pk=node_id)
    root_ou   = request.user.departament
    #children  = root_ou.get_children()
    children  = root_ou.get_family()
    children  = children[1:] # исключаем последний элемент

    if request.method == 'POST':
        data_in_post = request.POST
        parent_id = data_in_post['par_id']
        parent_id = int(parent_id)

        list_cplx = []
        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.cart_status = 2 # объект находится в пользовании
            m1.departament = get(parent_id)
            m1.cart_date_change = timezone.now()
            m1.save(update_fields=['departament', 'cart_status', 'cart_date_change'])
            
            list_cplx.append((m1.id, str(m1.cart_itm_name), m1.cart_number))
        sign_tr_cart_to_uses.send(sender=None, 
                                            list_cplx=list_cplx,
                                            request=request,
                                            org=str(get(parent_id)))
        return HttpResponseRedirect(reverse('stock'))
    return render(request, 'index/transfe_for_use.html', {'checked_cartr': checked_cartr, 'bulk': children})


class Use(CartridgesView):
    """Списки заправленных, новых картриджей на складе
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Use, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(Use, self).get(*args, **kwargs)
        self.context['view'] = 'use'
        try:
            root_ou   = self.request.user.departament
            children  = root_ou.get_family()
        except AttributeError:
            children = ''
        self.all_items = self.all_items.filter(departament__in=children).filter(cart_status=2)
        page_size = self.items_per_page()
        self.context['size_perpage'] = page_size
        self.context['cartrjs'] = self.pagination(self.all_items, page_size)
        return render(request, 'index/use.html', self.context)


class Empty(CartridgesView):
    """Списки заправленных, новых картриджей на складе
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Empty, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(Empty, self).get(*args, **kwargs)
        self.context['view'] = 'empty'
        root_ou = self.request.user.departament
        self.all_items = self.all_items.filter( Q(departament=root_ou) & Q(cart_status=3) )
        page_size = self.items_per_page()
        self.context['size_perpage'] = page_size
        self.context['cartrjs'] = self.pagination(self.all_items, page_size)
        return render(request, 'index/empty.html', self.context)


@login_required
def toner_refill(request):
    """
    """
    BreadcrumbsPath(request)
    city_id = request.GET.get('city', '')
    cities = CityM.objects.all()

    try:
        city_id = int(city_id)
    except ValueError:
        city_id = 0

    city = ""
    if city_id != 0:
        try:
            city = CityM.objects.get(pk=city_id)
        except CityM.DoesNotExist:
            raise Http404

    if city:
        firms = FirmTonerRefill.objects.filter(firm_city=city)
    else:
        firms = FirmTonerRefill.objects.all()
    # завершаем работу с пагинацией
    new_list = [{'id': 0, 'city_name': _('Select all')}]
    for i in cities:
        tmp_dict = {'id': i.id, 'city_name': i.city_name}
        new_list.append(tmp_dict)

    cities = None
    if city_id:
        city_url_parametr = '?city=' + str(city_id) + '&'
    else:
        city_url_parametr = '?'
    return render(request, 'index/toner_refill.html', {'cities': new_list,
                                                       'firms': firms,
                                                       'select': city_id,
                                                       'city_url': city_url_parametr,
                                                       })


@login_required
def add_city(request):
    """
    """
    back = BreadcrumbsPath(request).before_page(request)
    if request.method == 'POST':
        form_obj = CityF(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            m1 = CityM(city_name=data_in_post['city_name'])
            m1.save()
            return HttpResponseRedirect(reverse('index.views.toner_refill'))
    else:
        form_obj = CityF()
    return render(request, 'index/add_city.html', {'form': form_obj, 'back': back})


@login_required
def add_firm(request):
    """
    """
    back = BreadcrumbsPath(request).before_page(request)
    if request.method == 'POST':
        form_obj = FirmTonerRefillF(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            m1 = FirmTonerRefill(firm_name=data_in_post['firm_name'],
                                 firm_city=data_in_post['firm_city'],
                                 firm_contacts=data_in_post['firm_contacts'],
                                 firm_address=data_in_post['firm_address'],
                                 firm_comments=data_in_post['firm_comments'], )
            m1.save()
            messages.success(request, _('Firm "%(firm_name)s" success added.') % {'firm_name': data_in_post['firm_name']})
    else:
        form_obj = FirmTonerRefillF()
    return render(request, 'index/add_firm.html', {'form': form_obj, 'back': back})


@login_required
def edit_firm(request):
    """
    """
    back = BreadcrumbsPath(request).before_page(request)
    firm_id = request.GET.get('select', '')
    firm_id = firm_id.strip()
    if firm_id:
        try:
            firm_id = int(firm_id)
        except ValueError:
            firm_id = 0
    else:
        firm_id = 0

    if request.method == 'POST':
        form_obj = FirmTonerRefillF(request.POST)
        if form_obj.is_valid():
            all = form_obj.cleaned_data
            m1 = FirmTonerRefill.objects.get(pk=firm_id)
            m1.firm_name = all['firm_name']
            m1.firm_city = all['firm_city']
            m1.firm_contacts = all['firm_contacts']
            m1.firm_address = all['firm_address']
            m1.firm_comments = all['firm_comments']
            m1.save(update_fields=[
                'firm_name',
                'firm_city',
                'firm_contacts',
                'firm_address',
                'firm_comments'])

            return HttpResponseRedirect(reverse('index.views.toner_refill'))

    try:
        firm = FirmTonerRefill.objects.get(pk=firm_id)
    except FirmTonerRefill.DoesNotExist:
        raise Http404

    form_obj = FirmTonerRefillF(initial={
        'firm_name': firm.firm_name,
        'firm_city': firm.firm_city,
        'firm_contacts': firm.firm_contacts,
        'firm_address': firm.firm_address,
        'firm_comments': firm.firm_comments})
    return render(request, 'index/edit_firm.html', {'firm': firm, 'form': form_obj, 'back': back})


@login_required
@is_admin
def manage_users(request):
    """
    """
    usr = AnconUser.objects.all()
    return render(request, 'index/manage_users.html', {'urs': usr })


class At_work(CartridgesView):
    """Список картриджей находящихся на заправке.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(At_work, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(At_work, self).get(*args, **kwargs)
        self.context['view'] = 'at_work'
        self.all_items = self.all_items.filter(Q(cart_status=4) & Q(departament=self.request.user.departament))
        page_size = self.items_per_page()
        self.context['size_perpage'] = page_size
        self.context['cartrjs'] = self.pagination(self.all_items, page_size)
        return render(request, 'index/at_work.html', self.context)


class Basket(CartridgesView):
    """Список картриджей на выброс.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Basket, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(Basket, self).get(*args, **kwargs)
        self.context['view'] = 'basket'
        self.all_items = self.all_items.filter( (Q(cart_status=5) | Q(cart_status=6)) & Q(departament=self.request.user.departament) )
        page_size = self.items_per_page()
        self.context['size_perpage'] = page_size
        self.context['cartrjs'] = self.pagination(self.all_items, page_size)
        return render(request, 'index/basket.html', self.context)


@login_required
def transfe_to_basket(request):
    """Перемещаем расходники в корзинку.
    """
    checked_cartr = request.GET.get('select', '')
    action_type = request.GET.get('atype', '')
    back = BreadcrumbsPath(request).before_page(request)
    
    if action_type == '5':
        # перемещаем заправленный картридж в корзину
        cart_status = 5
    elif action_type == '6':
        # перемещаем пустой картридж в корзину
        cart_status = 6
    else:
        raise Http404

    tmp = ''
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartrw = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        tmp2 = []
        # преобразовываем айдишники в условные номера
        for cart_id in checked_cartr:
            tmp2.append(CartridgeItem.objects.get(pk=cart_id).cart_number)
        checked_cartr = str(tmp2)
        checked_cartr = checked_cartr[1:-1]
    
    if request.method == 'POST':
        list_cplx = []
        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.cart_status = cart_status  # в корзинку картриджи  
            m1.departament = request.user.departament
            m1.cart_date_change = timezone.now()
            m1.save(update_fields=['cart_status', 'departament', 'cart_date_change'])
            list_cplx.append((m1.id, str(m1.cart_itm_name), m1.cart_number))
        
        sign_tr_cart_to_basket.send(sender=None, list_cplx=list_cplx, request=request)

        return HttpResponseRedirect(reverse('stock'))
    return render(request, 'index/transfe_to_basket.html', {'checked_cartr': checked_cartr, 'back': back})


@login_required
def from_basket_to_stock(request):
    """Возвращаем обратно картридж из корзины на склад. Ну вдруг пользователь передумал.
    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]
    
    if request.method == 'POST':
        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            if m1.cart_status == 5:
                m1.cart_status = 1  # возвращаем обратно на склад заполненным    
            elif m1.cart_status == 6:
                m1.cart_status = 3  # возвращаем обратно на склад пустым    
            else:
                raise Http404
            m1.cart_date_change = timezone.now()
            m1.save(update_fields=['cart_status', 'cart_date_change'])
        return HttpResponseRedirect(reverse('basket'))
    return render(request, 'index/from_basket_to_stock.html', {'checked_cartr': checked_cartr})


@login_required
def transfer_to_firm(request):
    """Передача расходных материалов на заправку.
    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    firms = FirmTonerRefill.objects.all()
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        tmp2 = []
        # преобразовываем айдишники в условные номера
        for cart_id in checked_cartr:
            tmp2.append(CartridgeItem.objects.get(pk=cart_id).cart_number)
        checked_cartr = str(tmp2)
        checked_cartr = checked_cartr[1:-1]
        
    else:
        # если кто-то зашел на страницу не выбрав расходники
        return HttpResponseRedirect(reverse('empty'))       

    if request.method == 'POST':
        
        try:
            firmid = int(request.POST['firm'])
            if firmid == 0:
                raise ValueError
        except ValueError:
            messages.error(request, _('You input not correct firm name'))
            return render(request, 'index/transfer_to_firm.html', {'checked_cartr': checked_cartr, 
                                                                    'firms' : firms, 
                                                                })            
        else:
            list_cplx = []
            select_firm = FirmTonerRefill.objects.get(pk=firmid) 
            gen_act = request.POST.get('gen_act', '') # если чекбокс установлен, то метод вернет on
            if gen_act == 'on':
                from docs.models import SCDoc
                # генерируем акт передачи
                jsoning_list = []
                for inx in tmp:
                    cart_number = CartridgeItem.objects.get(pk=inx).cart_number
                    cart_name = CartridgeItem.objects.get(pk=inx).cart_itm_name
                    jsoning_list.append([cart_number, str(cart_name)])
                jsoning_list = json.dumps(jsoning_list)
                
                # генерируем номер акта передачи на основе даты и его порядкового номера
                act_docs = SCDoc.objects.filter(departament=request.user.departament).filter(doc_type=3).count()
                if act_docs:
                    act_docs   = act_docs + 1
                    act_number = str(timezone.now().year) + '_' + str(act_docs)
                else:
                    act_number = str(timezone.now().year) + '_1'

                act_doc = SCDoc(number=act_number,
                                date=timezone.now(),
                                firm=select_firm,
                                title='Act',
                                short_cont=jsoning_list,
                                departament=request.user.departament,
                                doc_type=3,
                                user=str(request.user.fio),)
                act_doc.save()

            for inx in tmp:
                m1 = CartridgeItem.objects.get(pk=inx)
                m1.cart_status = 4 # находится на заправке
                m1.filled_firm = select_firm
                m1.cart_date_change = timezone.now()
                m1.save(update_fields=['filled_firm', 'cart_status', 'cart_date_change'])
                list_cplx.append((m1.pk, str(m1.cart_itm_name), m1.cart_number))
            
            sign_tr_empty_cart_to_firm.send(sender=None, 
                                            list_cplx=list_cplx, 
                                            request=request, 
                                            firm=str(select_firm))
        return HttpResponseRedirect(reverse('empty'))
    return render(request, 'index/transfer_to_firm.html', {'checked_cartr': checked_cartr, 
                                                            'firms' : firms, 
                                                            })


@login_required
def from_firm_to_stock(request):
    """Возврашаем заправленные расходники обратно на базу.
    """
    back = BreadcrumbsPath(request).before_page(request)
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    list_cart = []
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        for cart_id in tmp:
            list_cart.append(CartridgeItem.objects.get(pk=cart_id))
        list_length = len(list_cart) 
        # преобразуем список в строку, для корректного отображения на html странице
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]
    else:
        # если кто-то зашел на страницу не выбрав расходники
        return HttpResponseRedirect(reverse('at_work'))        

    if request.method == 'POST':
        list_cplx = []
        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            filled_firm = str(m1.filled_firm)
            m1.filled_firm = None
            m1.cart_status = 1
            m1.cart_date_change = timezone.now()
            m1.cart_number_refills = int(m1.cart_number_refills) + 1
            m1.save(update_fields=['filled_firm', 'cart_status', 'cart_number_refills', 'cart_date_change'])
            repair_actions = request.POST.getlist('cart_'+str(inx))
            list_cplx.append((m1.id, str(m1.cart_itm_name), filled_firm, repair_actions, m1.cart_number))

        sign_tr_filled_cart_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
        return HttpResponseRedirect(reverse('at_work'))
    return render(request, 'index/from_firm_to_stock.html', {'checked_cartr': checked_cartr, 
                                                            'list_cart': list_cart, 
                                                            'list_length': list_length, 
                                                            'back': back})

def bad_browser(request):
    """Сообщение о необходимости обновить браузер.
    """
    return render(request, 'index/bad_browser.html')

@login_required
def edit_cartridge_comment(request):
    """Добавляем комментарий к картриджу.
    """
    item_id = request.GET.get('id', '')
    back    = BreadcrumbsPath(request).before_page(request)
    try:
        item_id = int(item_id)
    except ValueError:
        item_id = 0
    try:
        cartridge_object = CartridgeItem.objects.get(pk=item_id)
    except CartridgeItem.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = EditCommentForm(data=request.POST)
        if form.is_valid():
            cartridge_object.comment = form.cleaned_data.get('comment')
            cartridge_object.save()
            print('back=', back)
            return HttpResponseRedirect(back)
    else:
        comment = cartridge_object.comment
        form = EditCommentForm(initial = {'comment': comment})
    return render(request, 'index/edit_cartridge_comment.html', {'form': form, 'back': back})


def handler404(request):
    if request.user.is_authenticated():
        response = render(request, 'index/404.html', {})
        response.status_code = 404
        return response
    else:
        return HttpResponse(_('Page not found!'), status_code=404)
    

def handler500(request):
    response = render(request, 'index/500.html', {})
    response.status_code = 500
    return response
    