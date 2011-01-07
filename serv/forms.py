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


from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django import forms
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.shortcuts import get_object_or_404
from django.conf import settings

import urllib

from serv.models import Service, Area, Category, Transfer
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
        model = Service
        exclude = ('creator', 'pub_date', 'is_active')

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['area'].empty_label = _("Todas")
        self.fields['description'].help_text = _(u"Sugerencia: no introduzcas"
            u" datos personales a los que no quieras que cualquiera pueda"
            u" acceder, para ese fin utiliza mensajes privados.")

    def clean_offer(self):
        offer = self.cleaned_data.get("is_offer", "0")
        return bool(offer)


class ListServicesForm(forms.Form):
    TYPE_CHOICES = (
        ('0', '---------'),
        ('1', _('oferta')),
        ('2', _('demanda')),
    )
    USER_CHOICES = (
        ('0', _('---------')),
        ('1', _(u'se conectó hace menos de un día')),
        ('2', _(u'se conectó hace menos de una semana')),
        ('3', _(u'se conectó hace menos de 1 mes')),
        ('4', _(u'se conectó hace menos de 3 meses')),
        ('5', _(u'se conectó hace menos de 6 meses')),
        ('6', _(u'se conectó hace menos de 1 año')),
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
        self.fields['category'].queryset = Category.objects.all()
        self.fields['area'].queryset = Area.objects.all()

    def as_url_args(self):
        return urllib.urlencode(self.data)

class NewTransferForm(forms.ModelForm):
    CREDITS_CHOICES = (
        ('30', _('media hora')),
        ('60', _('1 hora')),
        ('90', _('1 hora y media')),
        ('120', _('2 horas')),
        ('150', _('2 horas y media')),
        ('180', _('3 horas')),
        ('210', _('3 horas y media')),
        ('240', _('4 horas')),
        ('270', _('4 horas y media')),
        ('300', _('5 horas')),
        ('330', _('5 horas y media')),
        ('360', _('6 horas')),
        ('390', _('6 horas y media')),
    )
    OFFER_CHOICES = (
        ('0', _(u'dar créditos')),
        ('1', _(u'solicitar créditos')),
    )
    username = forms.CharField(label=_(u"Nombre de usuario"), help_text=_(
        u"Nombre del usuario que recibirá o al que se le solicitan"
        u" los créditos a transferir"), required=True)

    credits = CustomCharField(label=_(u"Créditos"),
        widget=forms.Select(choices=CREDITS_CHOICES), required=True)

    service_type = CustomCharField(label=_("Tipo de servicio"),
            help_text=_(u"debes elegir si recibes o solicitas"
            u" créditos con esta transferencia"),
            widget=forms.Select(choices=OFFER_CHOICES))

    class Meta:
        model = Transfer
        fields = ['description', 'credits']

    def clean_credits(self):
        credits = self.cleaned_data.get("credits", "30")
        return int(credits)

    def clean_username(self):
        from user.models import Profile
        username = self.cleaned_data.get("username", "")
        try:
            self.user = get_object_or_404(Profile, username=username)
        except Exception, e:
            raise forms.ValidationError(_(u"No existe un usuario con"
                u" ese nombre."))


class AddTransferForm(forms.ModelForm):
    CREDITS_CHOICES = (
        ('30', _('media hora')),
        ('60', _('1 hora')),
        ('90', _('1 hora y media')),
        ('120', _('2 horas')),
        ('150', _('2 horas y media')),
        ('180', _('3 horas')),
        ('210', _('3 horas y media')),
        ('240', _('4 horas')),
        ('270', _('4 horas y media')),
        ('300', _('5 horas')),
        ('330', _('5 horas y media')),
        ('360', _('6 horas')),
        ('390', _('6 horas y media')),
    )

    credits = CustomCharField(label=_(u"Créditos"),
        widget=forms.Select(choices=CREDITS_CHOICES), required=True)

    class Meta:
        model = Transfer
        fields = ['description', 'credits']

    def clean_credits(self):
        credits = self.cleaned_data.get("credits", "30")
        return int(credits)

class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
