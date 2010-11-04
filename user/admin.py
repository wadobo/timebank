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

from django.contrib.auth.admin import UserAdmin
from models import Profile
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect

class ExtraProfileInline(admin.StackedInline):
    model = Profile
    fieldsets = (('Datos Extra', {
        'fields': ('birth_date', 'address', 'balance')
    }),)
    list_display = ('birth_date', 'address', 'balance')

def send_email_action(profile_admin, request, queryset):
    return redirect('user-send-email-to-all')
send_email_action.short_description = _("Enviar email a todos los usuarios")

class ProfileAdmin(UserAdmin):
    inlines = [
        ExtraProfileInline,
    ]
    actions = [send_email_action]

    def save_model(self, request, model, form, change):
        '''
        Will send activation emails when appropiate
        '''
        if not change:
            model.save()
            return

        old_model = Profile.objects.filter(id=model.id)[0]
        if model.is_active == True and old_model.is_active == False:
            # user activated, send activation email
            current_site = Site.objects.get_current()
            title = _("Bienvenido a %s, %s") % (settings.SITE_NAME,
                model.username)
            message = _(u"Enhorabuena %s!\n"
            u"Los adminitradores han aceptado tu solicitud de registro, "
            u"¡ahora ya puedes comenzar a colaborar con los demás en "
            u"http://%s/.\n\n- El equipo de %s.") %\
                (model.username, current_site.domain, settings.SITE_NAME)
            send_mail(title, message, settings.DEFAULT_FROM_EMAIL,
                [model.email])

        model.save()

admin.site.register(Profile, ProfileAdmin)
admin.site.unregister(User)
