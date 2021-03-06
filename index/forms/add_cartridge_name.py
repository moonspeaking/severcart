# -*- coding:utf-8 -*-

from django import forms
from index.models import CartridgeItemName
from django.utils.translation import ugettext_lazy as _

class AddCartridgeName(forms.ModelForm):
    class Meta:
        model = CartridgeItemName
        fields = ['cart_itm_name', 'cart_itm_type']

    def clean_cart_itm_name(self):
        """проверяем данные на наличие дублей.
        """
        data = self.cleaned_data.get('cart_itm_name').strip()
        search_type = CartridgeItemName.objects.filter(cart_itm_name=data)
        if search_type:
            raise forms.ValidationError(_('This name already exists!'))            
        else:
            return data
