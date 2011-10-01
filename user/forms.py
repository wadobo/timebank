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

from tinymce.widgets import TinyMCE

from models import Profile
from messages.models import Message
from utils import (FormCharField, FormEmailField, FormDateField,
    FormCaptchaField)
from  serv.forms import CustomCharField

class RegisterForm(UserCreationForm):
    birth_date = FormDateField(label=_("Birth date"),
        input_formats=("%d/%m/%Y",))

    first_name = FormCharField(label=_("Name"), required=True, max_length=30)
    last_name = FormCharField(label=_("Last name"), required=True, max_length=30)
    email = FormEmailField(label=_("Email address"), required=True)
    address = FormCharField(label=_("Address"), required=True,
        max_length=100, help_text=_("Example: Avda. Molina, 12, Sevilla"))
    description = FormCharField(label=_("Personal description"), required=True,
        max_length=300, widget=forms.Textarea())
    land_line = FormCharField(label=_("Land line"), max_length=20,
        required=False, help_text="Example: 954 123 111")
    mobile_tlf = FormCharField(label=_("Mobile Telephone"), max_length=20,
        required=False, help_text="Example: 651 333 111")
    captcha = FormCaptchaField()

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', 'email', 'address', 'birth_date', 'description', 'land_line', 'mobile_tlf')

class EditProfileForm(forms.ModelForm):
    photo = forms.ImageField(label=_("Avatar"), required=False)
    birth_date = FormDateField(label=_("Birth date"),
        input_formats=("%d/%m/%Y",))

    first_name = FormCharField(label=_("Name"), required=True,
        max_length=30)
    last_name = FormCharField(label=_("Last name"), required=True, max_length=30)
    email = FormEmailField(label=_("Email address"), required=True)
    address = FormCharField(label=_("Address"), required=True,
        max_length=100, help_text=_("Example: Avda. Molina, 12, Sevilla"))
    description = FormCharField(label=_("Personal description"), required=True,
        max_length=300, widget=forms.Textarea())
    password1 = forms.CharField(label=_("Current password"),
        widget=forms.PasswordInput, required=True,
        help_text=_("Enter your current password to check your identity"))
    land_line = FormCharField(label=_("Land line"), max_length=20,
        required=False, help_text="Example: 954 123 111")
    mobile_tlf = FormCharField(label=_("Mobile telephone"), max_length=20,
        required=False, help_text="Example: 651 333 111")

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
        fields = ('photo', 'first_name', 'last_name', 'email', 'address',  'birth_date',
            'description', 'land_line', 'mobile_tlf', 'email_updates')

class RemoveForm(forms.Form):
    reason = FormCharField(label=_("Reason"), required=True,
        min_length=10, max_length=300, widget=forms.Textarea(),
        help_text=_("Have we done something wrong? Please tell us why you want"
            "rmeove your user."))

class PublicMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("body",)

class FindPeopleForm(forms.Form):
    USER_CHOICES = (
        ('0', _('---------')),
        ('1', _(u'less than 24 hours ago')),
        ('2', _(u'less than one week ago')),
        ('3', _(u'less than one month ago')),
        ('4', _(u'less than 3 months ago')),
        ('5', _(u'less than 6 months ago')),
        ('6', _(u'less than one year ago')),
    )

    user_status = CustomCharField(label=_("User connected"),
        widget=forms.Select(choices=USER_CHOICES), required=False)
    username = forms.CharField(label=_("Username"), required=False)

    def as_url_args(self):
        import urllib
        return urllib.urlencode(self.data)

class FindPeople4AdminsForm(FindPeopleForm):
    USER_CHOICES = FindPeopleForm.USER_CHOICES + (
        ('7', _(u'more than a week ago')),
        ('8', _(u'more than one month ago')),
        ('9', _(u'more than 3 months ago')),
        ('10', _(u'more than 6 months ago')),
        ('11', _(u'more than one year')),
    )
    user_status = CustomCharField(label=_("User connected"),
        widget=forms.Select(choices=USER_CHOICES), required=False)
    without_services = forms.BooleanField(label=_("Without services"), required=False)

class SendEmailToAllForm(forms.Form):
    subject = forms.CharField(label=_(u'Subject'), required=True)
    message = forms.CharField(label=_(u'Message body'), required=True,
        widget=forms.Textarea)
