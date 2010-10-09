# -*- coding: utf-8 -*-
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

from django import forms
from django.utils.translation import ugettext_lazy as _
from utils import FormCharField, FormEmailField, FormCaptchaField

class AnonymousContactForm(forms.Form):
    '''
    Contact form that can be used when the user is not logged in. Anyone
    can send it. Hence, we need information about the sender to be able to get
    back to it, and a captcha to avoid spammers.
    '''
    name = FormCharField(label=_("Nombre y apellidos"), required=True,
        min_length=3, max_length=30)
    email = FormEmailField(label=_(u"Tu email de contacto"), required=True)
    subject = FormCharField(label=_("Asunto"), required=True,
        min_length=5, max_length=200)
    message = FormCharField(label=_(u"Mensaje"), required=True,
        min_length=5, max_length=1000, widget=forms.Textarea())
    captcha = FormCaptchaField()

class ContactForm(forms.Form):
    '''
    Simple contact form to be used for logged in users.
    '''
    subject = FormCharField(label=_("Asunto"), required=True,
        min_length=5, max_length=200)
    message = FormCharField(label=_(u"Mensaje"), required=True,
        min_length=5, max_length=1000, widget=forms.Textarea())
