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
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _


from models import Profile
from messages.models import Message
from utils import FormCharField, FormEmailField, FormDateField
from  serv.forms import CustomCharField

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
    land_line = FormCharField(label=_(u"Teléfono fijo"), max_length=20,
        required=False, help_text="Ejemplo: 954 123 111")
    mobile_tlf = FormCharField(label=_(u"Teléfono móvil"), max_length=20,
        required=False, help_text="Ejemplo: 651 333 111")

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', 'email', 'address', 'birth_date', 'description', 'land_line', 'mobile_tlf')

class EditProfileForm(forms.ModelForm):
    birth_date = FormDateField(label=_("Fecha de Nacimiento"),
        input_formats=("%d/%m/%Y",))

    first_name = FormCharField(label=_("Nombre propio"), required=True,
        max_length=30)
    last_name = FormCharField(label=_("Apellidos"), required=True, max_length=30)
    email = FormEmailField(label=_(u"Dirección de email"), required=True)
    address = FormCharField(label=_(u"Dirección física"), required=True,
        max_length=100, help_text=_(u"Ejemplo: Avda. Molina, 12, Sevilla"))
    description = FormCharField(label=_(u"Descripción personal"), required=True,
        max_length=300, widget=forms.Textarea())
    password1 = forms.CharField(label=_(u"Contraseña actual"),
        widget=forms.PasswordInput, required=True,
        help_text=_(u"Introduce tu contraseña actual para comprobar tu"
            " identidad."))
    land_line = FormCharField(label=_(u"Teléfono fijo"), max_length=20,
        required=False, help_text="Ejemplo: 954 123 111")
    mobile_tlf = FormCharField(label=_(u"Teléfono móvil"), max_length=20,
        required=False, help_text="Ejemplo: 651 333 111")

    def __init__(self, request, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean_password1(self):
        password1 = self.cleaned_data["password1"]
        if not self.request.user.check_password(password1):
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password1

    class Meta:
        model = Profile
        hidden = ()
        fields = ('first_name', 'last_name', 'email', 'address',
        'birth_date', 'description', 'land_line', 'mobile_tlf')

class RemoveForm(forms.Form):
    reason = FormCharField(label=_(u"Razón"), required=True,
        min_length=10, max_length=300, widget=forms.Textarea(),
        help_text=_(u"¿Hemos hecho algo mal? Por favor díganos la razón por"
            u"la que quiere darse de baja."))

class PublicMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("body",)

class FindPeopleForm(forms.Form):
    USER_CHOICES = (
        ('0', _('---------')),
        ('1', _(u'se conectó hoy')),
        ('2', _(u'se conectó esta semana')),
        ('3', _(u'se conectó este mes')),
        ('4', _(u'se conectó este año')),
    )

    user_status = CustomCharField(label=_("Estado del usuario"),
        widget=forms.Select(choices=USER_CHOICES), required=False)
    username = forms.CharField(label=_("Nombre de usuario"), required=False)

    def as_url_args(self):
        import urllib
        return urllib.urlencode(self.data)

