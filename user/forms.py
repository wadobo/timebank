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

from models import Profile
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from utils import FormCharField, FormEmailField, FormDateField

class RegisterForm(UserCreationForm):
    birth_date = FormDateField(label=_("Fecha de Nacimiento"),
        input_formats=("%d/%m/%Y",))

    first_name = FormCharField(label=_("Nombre propio"), required=True, max_length=30)
    last_name = FormCharField(label=_("Apellidos"), required=True, max_length=30)
    email = FormEmailField(label=_(u"Dirección de email"), required=True)
    address = FormCharField(label=_(u"Dirección física"), required=True,
        max_length=100, help_text=_(u"Ejemplo: Avda. Molina, 12, Sevilla"))
    description = FormCharField(label=_(u"Descripción personal"), required=True,
        max_length=300, widget=forms.Textarea())

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', 'email', 'address', 'birth_date', 'description')
