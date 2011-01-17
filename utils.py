# -*- coding: utf-8 -*-
# Copyright (C) 2010 Daniel García Moreno <dani AT danigm DOT net>
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

from django.shortcuts import redirect
from django.http import HttpResponse as response
from django.http import HttpResponseNotAllowed
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils.translation import gettext as _
from django import forms
from datetime import datetime, date
from django.utils import formats
from django.conf import settings
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from recaptcha.client import captcha

from flashmsg import flash

import types

class SlashGETPOST(type):
    def __init__(cls, name, bases, dct):
        # GET and POST now are __GET__ and __POST__ to avoid confusion with
        # request.GET and request.POST
        type.__init__(cls, name, bases, dct)
        av_methods = ['GET', 'POST', 'PUT', 'DELETE']
        methods = [x for x in dct if isinstance(dct[x], types.FunctionType) and x in av_methods]
        for m in methods:
            setattr(cls, '__%s__' % m, dct[m])
            delattr(cls, m)


class ViewClass(object):
    '''
    Used to create views with classes with GET and POST methods instead of
    using functions.
    '''
    __metaclass__ = SlashGETPOST

    available_methods = ['POST', 'GET', 'PUT', 'DELETE']

    def __call__(self, request, *args, **kwargs):
        self.request = request
        self.methods = [method.replace('_', '') for method in dir(self)\
            if callable(getattr(self, method)) and\
               method.replace('_', '') in self.available_methods]

        if request.method in self.methods:
            try:
                view = getattr(self, '__' + request.method + '__')
            except AttributeError:
                view = getattr(self, request.method)
            return view(*args, **kwargs)
        else:
            return HttpResponseNotAllowed(self.methods)

    def context_response(self, *args, **kwargs):
        kwargs['context_instance'] = RequestContext(self.request)
        return render_to_response(*args, **kwargs)

    def flash(self, msg, msg_class='info', title=None):
        '''
        Add msg to session flash stack
        '''

        stack = self.request.session.get('flash', None)
        if not stack:
            stack = flash.Stack()
        msg = flash.Msg(msg, msg_class, title)
        stack.insert(0, msg)
        self.request.session['flash'] = stack

    def __getattr__(self, value):
        # we work as request to make django decorators happy.
        if value != 'request' and hasattr(self, 'request'):
            return getattr(self.request, value)
        else:
            raise AttributeError, value

def login_required(fn):
    '''
    Login required decorator, it works similarly as the login_required decorator
    from django.auth.decorators.
    NOTE it can only be used inside a ViewClass. It WONT work in typical django
    function views.
    '''
    def wrapper(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            self.flash(_(u'You must be registered to enter in'
                u' <a href="%(link)s">%(link_text)s</a>. If you want to join'
                u' us now or enter with your user clic in the box at the '
                u' left.') %\
                {
                    'link': self.request.get_full_path(),
                    'link_text': self.request.get_full_path()
                })
            return redirect('user-register')
        return fn(self, *args, **kwargs)
    return wrapper

class FormCharField(forms.CharField):
    '''
    Like forms.CharField with automatic help_text which shows the restrictions
    imposed in the field.
    '''
    def __init__(self, *args, **kwargs):
        super(FormCharField, self).__init__(*args, **kwargs)
        self.update_auto_help_text()

    def get_help_text(self):
        return unicode(self._auto_help_text) + unicode(self._help_text)

    def set_help_text(self, help_text):
        self._help_text = help_text

    def update_auto_help_text(self):
        self._auto_help_text = u''
        if self.required:
            self._auto_help_text += _(u"Required. ")
        else:
            self._auto_help_text += _(u"Optional. ")
        if self.max_length and self.min_length:
            self._auto_help_text += _(u"From %(from)d to %(to)d characters. ")\
                % {'from': self.min_length, 'to': self.max_length}
        elif self.max_length:
            self._auto_help_text += _(u"Up to %d characters. ")\
                % self.max_length
        elif self.min_length:
            self._auto_help_text += _(u"Minimum %d characters. ")\
                % self.min_length

    help_text = property(get_help_text, set_help_text)

class FormEmailField(forms.EmailField):
    '''
    Like forms.EmailField with automatic help_text which shows the restrictions
    imposed in the field.
    '''
    def __init__(self, *args, **kwargs):
        super(FormEmailField, self).__init__(*args, **kwargs)
        self.update_auto_help_text()

    def get_help_text(self):
        return unicode(self._auto_help_text) + unicode(self._help_text)

    def set_help_text(self, help_text):
        self._help_text = help_text

    def update_auto_help_text(self):
        self._auto_help_text = u''
        if self.required:
            self._auto_help_text += _(u"Requeried. ")
        else:
            self._auto_help_text += _(u"Optional. ")
        self._auto_help_text += _(u" Example: name@example.com")

    help_text = property(get_help_text, set_help_text)


class FormDateField(forms.DateField):
    '''
    Like forms.DateField with automatic help_text which shows the restrictions
    imposed in the field.
    '''
    def __init__(self, *args, **kwargs):
        super(FormDateField, self).__init__(*args, **kwargs)
        self.update_auto_help_text()

    def prepare_value(self, value):
        if isinstance(value, date):
            format = self.input_formats[0] or formats.get_format('DATE_INPUT_FORMATS')[0]
            return value.strftime(format)
        else:
            return value

    def get_help_text(self):
        return unicode(self._auto_help_text) + unicode(self._help_text)

    def set_help_text(self, help_text):
        self._help_text = help_text

    def update_auto_help_text(self):
        self._auto_help_text = u''
        if self.required:
            self._auto_help_text += _(u"Required. Example(s): ")
        else:
            self._auto_help_text += _(u"Optional. Example(s): ")

        the_date = datetime(1986, 9, 17).date()

        self._auto_help_text +=  ', '.join([the_date.strftime(format)
            for format in self.input_formats or
                formats.get_format('DATE_INPUT_FORMATS')])

    help_text = property(get_help_text, set_help_text)

class FormCaptchaWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None):
        return mark_safe(u'%s' % captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY))

    def value_from_datadict(self, data, files, name):
        return [data.get('recaptcha_challenge_field', None),
            data.get('recaptcha_response_field', None)]

class FormCaptchaField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.widget = FormCaptchaWidget
        self.required = True
        super(FormCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(FormCaptchaField, self).clean(values[1])
        recaptcha_challenge_value = smart_unicode(values[0])
        recaptcha_response_value = smart_unicode(values[1])
        check_captcha = captcha.submit(recaptcha_challenge_value,
            recaptcha_response_value, settings.RECAPTCHA_PRIVATE_KEY, {})
        if not check_captcha.is_valid:
            raise forms.util.ValidationError(_(u'Invalid captcha'))
        return values[0]
