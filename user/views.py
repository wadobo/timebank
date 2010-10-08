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
from utils import ViewClass
from forms import RegisterForm
from django.core.mail import send_mail
from settings import SITE_NAME, DEFAULT_FROM_EMAIL, ADMINS

class Register(ViewClass):
    def GET(self):
        form = RegisterForm()
        return self.context_response('user/register.html', {'form': form})

    def POST(self):
        form = RegisterForm(self.request)
        if not form.is_valid():
            return self.context_response('user/register.html', {'form': form})

        # Register user
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        # Send email
        title = _("[%s] Usuario %s registrado") % (SITE_NAME, user.username)
        message = _("Se ha registrado un nuevo usuario con nombre de usuario:"\
        " %s . Revise sus datos y delo de alta.") % user.username
        send_mail(title, message, DEFAULT_FROM_EMAIL,
            [user.email], fail_silently=True)

        return self.context_response('user/registerdone.html', {
            'new_user': new_user})

register = Register()
