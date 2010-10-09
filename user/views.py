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

from django.shortcuts import redirect
from django.conf import settings
from django.contrib.sites.models import Site
from utils import ViewClass
from forms import RegisterForm
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login as django_login

from settings import SITE_NAME, DEFAULT_FROM_EMAIL, ADMINS

class Register(ViewClass):
    def GET(self):
        form = RegisterForm()
        return self.context_response('user/register.html', {'form': form})

    def POST(self):
        form = RegisterForm(self.request.POST)
        if not form.is_valid():
            return self.context_response('user/register.html', {'form': form})

        # Register user
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        # Send an email to admins and another to the user
        title = _("[%s] Usuario %s registrado") % (SITE_NAME,
            new_user.username)
        message = _("Se ha registrado un nuevo usuario con nombre de usuario "\
        " %s . Revise sus datos y delo de alta.") % new_user.username
        send_mail(title, message, DEFAULT_FROM_EMAIL, ADMINS,
            fail_silently=True)

        current_site = Site.objects.get_current()
        title = _("Te has registrado como %s en %s") % (new_user.username,
            SITE_NAME)
        message = _(u"Hola %s!\n Te acabas de registrar en http://%s/."
            u"Próximamente la creación de tu usuario será revisada por"
            u"nuestros administradores y si todo está correcto, activaremos tu"
            u" usuario y podrás comenzar a participar en nuestra comunidad."
            u"\n\n- El Equipo de %s.") %\
            (new_user.username, current_site.domain, SITE_NAME)
        send_mail(title, message, DEFAULT_FROM_EMAIL, ADMINS,
            fail_silently=True)

        return self.context_response('user/registerdone.html', {
            'new_user': new_user})


class Login(ViewClass):
    def GET(self):
        return redirect('main.views.index')

    def POST(self, *args):
        username = self.request.POST['username']
        password = self.request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                django_login(self.request, user)
                self.flash(_("Bienvenido %s") % user.username)
            else:
                self.flash(_(u"Tu cuenta está deshabilitada, "
                             u"contacta con los administradores"), "error")
        else:
            self.flash(_(u"Nombre de usuario o contrase&ntilde;a inválidos"), "error")
        return redirect('main.views.index')


login = Login()
register = Register()
