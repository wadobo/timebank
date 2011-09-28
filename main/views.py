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

from django.shortcuts import render_to_response, redirect
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import signals
from django.views.i18n import set_language as django_set_language
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse

from utils import ViewClass, login_required, mail_owners, I18nString
from forms import AnonymousContactForm, ContactForm
from serv.models import Service
from messages.utils import new_transfer_email

class Index(ViewClass):
    def GET(self):
        services = Service.objects.filter(is_active=True)
        paginator = Paginator(services, 5)
        services = paginator.page(1)
        return self.context_response('main/index.html', {'show_news': True,
        'services': services})


class Contact(ViewClass):
    def GET(self):
        if self.request.user.is_authenticated():
            form = ContactForm()
        else:
            form = AnonymousContactForm()
        return self.context_response('main/contact.html', {'form': form,
            'current_tab': 'contact'})

    def POST(self):
        if self.request.user.is_authenticated():
            form = ContactForm(self.request.POST)
        else:
            form = AnonymousContactForm(self.request.POST)
        if not form.is_valid():
            return self.context_response('main/contact.html', {'form': form,
            'current_tab': 'contact'})

        # Send an email to admins
        if self.request.user.is_authenticated():
            user = self.request.user
            subject = I18nString(_("[%(site_name)s] %(username)s: %(email_subject)s"), {
                'site_name': settings.SITE_NAME,
                'username': user.username,
                'email_subject': form.cleaned_data["subject"]
            })
            message = I18nString(_(u"Registered user %(username)s sends the following "\
            " message:\n%(message)s"), {
                'username': user.username,
                'message': form.cleaned_data["message"]
            })
        else:
            subject = I18nString(_("[%(site_name)s] %(email)s: %(email_subject)s"), {
                'site_name': settings.SITE_NAME,
                'email': form.cleaned_data["email"],
                'email_subject': form.cleaned_data["subject"]
            })
            message = I18nString(_("Registered user %(name)s whose email is %(email)s"\
                " sends the following message:\n%(message)s"), {
                    'name': form.cleaned_data["name"],
                    'email': form.cleaned_data["email"],
                    'message': form.cleaned_data["message"]
                })
        mail_owners(subject, message)

        self.flash(_("Mail sent, we'll answer you as soon as possible."))
        return redirect('main.views.index')


class ErrorHandler(ViewClass):
    def __init__(self, template, retcode=200):
        self.template = template
        self.retcode = retcode

    def GET(self):
        response = self.context_response(self.template, {})
        response.status_code = self.retcode
        return response

    def POST(self):
        return self.GET()

class SetLanguage(ViewClass):
    """
    Extends django's set_language view to save the user's language in his
    profile
    """

    def POST(self):
        if self.request.user.is_authenticated():
            self.request.user.lang_code = self.request.POST.get('language', None)
            self.request.user.save()

        return django_set_language(self.request)


class Report(ViewClass):
    def __init__(self, report=1):
        from main.management.commands.report import reports
        self.report = reports[report - 1]

    @user_passes_test(lambda u: u.is_superuser)
    def GET(self):
        return HttpResponse(self.report(), mimetype="application/x-download")


index = Index()
contact = Contact()
handler404 = ErrorHandler('404.html', retcode=404)
handler500 = ErrorHandler('500.html', retcode=500)
set_language = SetLanguage()
report1 = Report(1)
report2 = Report(2)
report3 = Report(3)
report4 = Report(4)
report5 = Report(5)
