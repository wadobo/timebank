# -*- coding: utf-8 -*-
# Copyright (C) 2009 Tim Gaggstatter <Tim.Gaggstatter AT gmx DOT net>
# Copyright (C) 2010 Eduardo Robles Elvira <edulix AT gmail DOT com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



from django.utils.translation import ugettext as _
from django import forms
import urllib
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.shortcuts import get_object_or_404
from django.conf import settings

from serv.models import (Servicio, ContactoIntercambio, MensajeI, Zona,
    Categoria, Transfer)
from messages.models import Message
from utils import FormCharField

class CustomCharField(forms.CharField):

    def prepare_value(self, data):
        if data:
            return str(int(data))
        else:
            return '0'


class ServiceForm(forms.ModelForm):

    OFFER_CHOICES = (
        ('0', _('demanda')),
        ('1', _('oferta')),
    )

    oferta = CustomCharField(label=_("Tipo de servicio"),
                             help_text=_("debe elegir si es una oferta "
                                       "(ofrece algo) o una demanda (solicita "
                                       "algo)"),
                             widget=forms.Select(choices=OFFER_CHOICES))

    class Meta:
        model = Servicio
        exclude = ('creador', 'pub_date', 'activo')

    def clean_offer(self):
        offer = self.cleaned_data.get("oferta", "0")
        return bool(offer)


class ListServicesForm(forms.Form):
    TYPE_CHOICES = (
        ('0', '---------'),
        ('1', _('oferta')),
        ('2', _('demanda')),
    )
    USER_CHOICES = (
        ('0', _('---------')),
        ('1', _(u'se conectó hoy')),
        ('2', _(u'se conectó esta semana')),
        ('3', _(u'se conectó este mes')),
        ('4', _(u'se conectó este año')),
    )

    mine = forms.BooleanField(label=_(u"Sólo listar mis servicios"), required=False)
    the_type = CustomCharField(label=_("Tipo de servicio"),
        widget=forms.Select(choices=TYPE_CHOICES), required=False)
    category = forms.ModelChoiceField(None, required=False, label=_(u"Categoría"))
    area = forms.ModelChoiceField(None, required=False, label=_("Zona"))
    user_status = CustomCharField(label=_("Estado del usuario"),
        widget=forms.Select(choices=USER_CHOICES), required=False)
    username = forms.CharField(label=_("Nombre de usuario"), required=False)

    def __init__(self,  *args, **kwargs):
        super(ListServicesForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Categoria.objects.all()
        self.fields['area'].queryset = Zona.objects.all()

    def as_url_args(self):
        return urllib.urlencode(self.data)

class AddTransferForm(forms.ModelForm):
    credits = FormCharField(label=_(u"Créditos"), required=True, max_length=3,
        help_text=_(u"En minutos. Ejemplo: 60, 30, 120"))

    class Meta:
        model = Transfer
        fields = ['description', 'is_public', 'credits']

    def clean_credits(self):
        credits = self.cleaned_data["credits"]
        try:
            credits = int(credits)
        except ValueError:
            raise forms.ValidationError(_(u"Número inválido"))
        if credits < 0 or credits > settings.MAX_CREDITS_PER_TRANSFER:
            raise forms.ValidationError(u"Límite de créditos sobrepasado")
        return credits

class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body', 'is_public']

class ContactoIForm(forms.ModelForm):

    class Meta:
        model = ContactoIntercambio


class MensajeIForm(forms.ModelForm):

    class Meta:
        model = MensajeI
        fields = ['contenido']

    def clean_contenido(self):
        conte = self.cleaned_data.get("contenido", "")
        if 1 > len(conte) or len(conte) > 400:
            raise forms.ValidationError("El comentario debe tener entre 1 "
                                        "y 400 caracteres y el actual tiene "
                                        "%s." % len(conte))
        return conte
