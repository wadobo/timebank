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
from django.utils.translation import ugettext as _
from django import forms
from datetime import datetime, date
from django.utils import formats
from django.conf import settings
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from recaptcha.client import captcha
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string

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
                ' <a href="%(link)s">%(link_text)s</a>. You might want to'
                ' <a href="%(join_url)s">join us now</a> or enter with your'
                ' user using the grey login box at the left.') %\
                {
                    'link': self.request.get_full_path(),
                    'link_text': self.request.get_full_path(),
                    'join_url': reverse('user-register')
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
        if not settings.SHOW_CAPTCHAS:
            return  _('Captcha disabled')
        return mark_safe(u'%s' % captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY))

    def value_from_datadict(self, data, files, name):
        if not settings.SHOW_CAPTCHAS:
            return "captcha disabled"
        return [data.get('recaptcha_challenge_field', None),
            data.get('recaptcha_response_field', None)]

class FormCaptchaField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.widget = FormCaptchaWidget
        self.required = True
        super(FormCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(FormCaptchaField, self).clean(values[1])
        if not settings.SHOW_CAPTCHAS:
            return values
        recaptcha_challenge_value = smart_unicode(values[0])
        recaptcha_response_value = smart_unicode(values[1])
        check_captcha = captcha.submit(recaptcha_challenge_value,
            recaptcha_response_value, settings.RECAPTCHA_PRIVATE_KEY, {})
        if not check_captcha.is_valid:
            raise forms.util.ValidationError(_(u'Invalid captcha'))
        return values[0]

def mail_owners(subject, message, fail_silently=False, connection=None):
    '''
    Sends a message to the owners, as defined by the OWNERS setting. Sends the
    email to the owners with the language in settings.LANGUAGE_CODE. Use
    ugettext_lazy if you want your message to be correctly translated.
    '''
    if not settings.OWNERS:
        return

    from django.utils import translation
    cur_language = translation.get_language()
    try:
        translation.activate(settings.LANGUAGE_CODE)

        EmailMessage(settings.EMAIL_SUBJECT_PREFIX + unicode(subject),
            unicode(message),
            settings.SERVER_EMAIL, [a[1] for a in settings.OWNERS],
            connection=connection
        ).send(fail_silently=fail_silently)

    finally:
        translation.activate(cur_language)

def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None):
    '''
    Sends an email to the given recipients' user list in their language. Use
    ugettext_lazy if you want the email to be correctly translated.
    '''
    from django.utils import translation
    from django.core.mail import send_mail as django_send_mail

    cur_language = translation.get_language()
    default_language = settings.LANGUAGE_CODE
    try:
        for recipient in recipient_list:
            print "language code: ", recipient.lang_code, default_language
            if recipient.lang_code:
                translation.activate(recipient.lang_code)
            else:
                translation.activate(default_language)

            django_send_mail(unicode(subject), unicode(message), from_email,
                [recipient.email,], fail_silently, auth_user, auth_password, connection)
    finally:
        translation.activate(cur_language)

class I18nString(object):
    '''
    This string is similar to ugettext_lazy because it doesn't render the string
    until needed, but improving this laziness, delaying this even when giving
    arguments and using a template_rendering.
    '''

    def __init__(self, message, args, render=False):
        '''
        Constructs a I18nString, either having a message to translate in
        english, or if render=True then message (first paramenter) is the
        path to the template to render.
        '''
        self.message = message
        self.args = args
        self.render = render

    def to_unicode(self, language_code=None):
        from django.utils import translation
        cur_language = translation.get_language()
        renderized_string = None
        try:
            if language_code:
                translation.activate(language_code)
            if self.render:
                renderized_string = render_to_string(self.message, self.args)
            else:
                renderized_string = self.message % self.args
        finally:
            if language_code:
                translation.activate(settings.LANGUAGE_CODE)
        return renderized_string

    def __unicode__(self):
        return self.to_unicode()
