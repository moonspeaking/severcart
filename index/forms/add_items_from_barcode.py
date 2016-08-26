# -*- coding:utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from index.models import CartridgeItemName
from docs.models  import SCDoc
from storages.models import Storages


class AddItemsFromBarCodeScanner(forms.Form):
    cartNumber = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'readonly': True, 'class': 'loc'}), required=True)

    cartName = forms.ModelChoiceField(queryset=CartridgeItemName.objects.all(),
                                      error_messages={'required': _('Required field.')},
                                      empty_label=' ',
                                      required=True,
                                      )
    
    doc = forms.ModelChoiceField(queryset=SCDoc.objects.filter(), required=False)
    storages = forms.ModelChoiceField(queryset=Storages.objects.filter(), label=_('Storage'))


    required_css_class = 'required'

    def clean_cartName(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('cartName', ''):
            raise ValidationError(_('Required field.'))
        return self.cleaned_data.get('cartName', '')

    def clean_doc(self):
        """
        """
        if not self.cleaned_data.get('doc', 0):
            return 0
        
        doc_id = self.cleaned_data.get('doc')
        return doc_id.pk

    def clean_storages(self):
        """
        """
        if not self.cleaned_data.get('storages', 0):
            raise ValidationError(_('Required field.'))
        
        return self.cleaned_data.get('storages')
