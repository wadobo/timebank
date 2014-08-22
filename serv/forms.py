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
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.shortcuts import get_object_or_404
from django.conf import settings

import urllib

from serv.models import Service, Area, Category, Transfer
from tbmessages.models import Message
from timebank.utils import FormCharField

class CustomCharField(forms.CharField):

    def prepare_value(self, data):
        if data:
            return str(int(data))
        else:
            return '0'


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        exclude = ('creator', 'pub_date', 'is_active')
        widgets = {
            'is_offer': forms.Select
        }


    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['area'].empty_label = _("All")
        self.fields['description'].help_text = _("Tip: do not introduce"
            " personal data that you don't want to make public, use private"
            " messages for that.")


class ListServicesForm(forms.Form):
    TYPE_CHOICES = (
        ('0', '---------'),
        ('1', _('offer')),
        ('2', _('demand')),
    )
    USER_CHOICES = (
        ('0', _('---------')),
        ('1', _(u'connected less than a day ago')),
        ('2', _(u'connected less than a week ago')),
        ('3', _(u'connected less than a month ago')),
        ('4', _(u'connected less than 3 months ago')),
        ('5', _(u'connected less than 6 months ago')),
        ('6', _(u'connected less than a year ago')),
    )

    mine = forms.BooleanField(label=_("Only list my services"), required=False)
    the_type = CustomCharField(label=_("Service type"),
        widget=forms.Select(choices=TYPE_CHOICES), required=False)
    category = forms.ModelChoiceField(None, required=False, label=_("Category"))
    area = forms.ModelChoiceField(None, required=False, label=_("Area"))
    user_status = CustomCharField(label=_("User status"),
        widget=forms.Select(choices=USER_CHOICES), required=False)
    username = forms.CharField(label=_("Username"), required=False)
    text = forms.CharField(label=_("Text"), required=False)

    def __init__(self,  *args, **kwargs):
        super(ListServicesForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['area'].queryset = Area.objects.all()

    def as_url_args(self):
        return urllib.urlencode(self.data)

class NewTransferForm(forms.ModelForm):
    CREDITS_CHOICES = (
        ('30', _('half hour')),
        ('60', _('1 hour')),
        ('90', _('1 hour and half')),
        ('120', _('2 hours')),
        ('150', _('2 hours and half')),
        ('180', _('3 hours')),
        ('210', _('3 hours and half')),
        ('240', _('4 hours')),
        ('270', _('4 hours and half')),
        ('300', _('5 hours')),
        ('330', _('5 hours and half')),
        ('360', _('6 hours')),
        ('390', _('6 hours and half')),
    )
    OFFER_CHOICES = (
        ('0', _(u'give credits')),
        ('1', _(u'ask for credits')),
    )
    username = forms.CharField(label=_("Username"), help_text=_(
        "Name the user who will receive or will be asked for the credits"
        " to transfer"), required=True)

    credits = CustomCharField(label=_("Credits"),
        widget=forms.Select(choices=CREDITS_CHOICES), required=True)

    service_type = CustomCharField(label=_("Service type"),
            help_text=_("Choose if you receive or ask for credits with"
            " this transfer"),
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
            raise forms.ValidationError(_("No user exists with this username."))


class AddTransferForm(forms.ModelForm):
    CREDITS_CHOICES = (
        ('30', _('half hour')),
        ('60', _('1 hour')),
        ('90', _('1 hour and half')),
        ('120', _('2 hours')),
        ('150', _('2 hours and half')),
        ('180', _('3 hours')),
        ('210', _('3 hours and half')),
        ('240', _('4 hours')),
        ('270', _('4 hours and half')),
        ('300', _('5 hours')),
        ('330', _('5 hours and half')),
        ('360', _('6 hours')),
        ('390', _('6 hours and half')),
    )

    credits = CustomCharField(label=_("Credits"),
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
