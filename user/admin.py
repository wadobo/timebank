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
from utils import send_mail, I18nString
from django.conf import settings
from django.shortcuts import redirect

class ExtraProfileInline(admin.StackedInline):
    model = Profile
    fieldsets = (('Extra data', {
        'fields': ('photo', 'birth_date', 'address', 'balance')
    }),)
    list_display = ('birth_date', 'address', 'balance')

def send_email_action(profile_admin, request, queryset):
    return redirect('user-send-email-to-all')
send_email_action.short_description = _("Send email to all users")


def activate_user_action(profile_admin, request, queryset):
    queryset.update(is_active=True)
activate_user_action.short_description = _("Activate users")


def deactivate_user_action(profile_admin, request, queryset):
    queryset.update(is_active=False)
deactivate_user_action.short_description = _("Deactivate users")

def reset_password_user_action(profile_admin, request, queryset):
    import random
    from string import letters
    from django.core.urlresolvers import reverse

    for u in queryset:
        pwd = ''.join(random.choice(letters) for i in range(8))
        u.set_password(pwd)
        u.save()

        current_site = Site.objects.get_current()
        title = I18nString(_("Your password has been reset for %(site_name)s"), {
            'site_name': settings.SITE_NAME,
            'username': u.username
        })
        message = I18nString(_(u" %(username)s!\n"
        u"The admins have reset your password, "
        u"You can enter in "
        u"http://%(url)s/ with the following credentials:\n\n"
        u"username: %(username)s\n"
        u"password: %(password)s\n\n"
        u"You can change your password in your profile:\n"
        u"http://%(url)s%(pwdchange)s"
        u"\n\n- The team of %(site_name)s."), {
            'username': u.username,
            'password': pwd,
            'url': current_site.domain,
            'pwdchange': reverse("user-password-change"),
            'site_name': settings.SITE_NAME
        })

        send_mail(title, message, settings.DEFAULT_FROM_EMAIL,
            [u], fail_silently=True)

reset_password_user_action.short_description = _("Reset password")


class ProfileAdmin(UserAdmin):
    inlines = [
        ExtraProfileInline,
    ]
    actions = [send_email_action, activate_user_action,
               deactivate_user_action,
               reset_password_user_action]
    list_display = ('username', 'email', 'get_full_name', 'last_login',
                    'is_active', 'is_staff', 'balance', 'karma')

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
            title = I18nString(_("Welcome to %(site_name)s, %(username)s"), {
                'site_name': settings.SITE_NAME,
                'username': model.username
            })
            message = I18nString(_(u"Congratulations %(username)s!\n"
            u"The admins have accepted your registration request, "
            u"now you can start collaborating in our community in  "
            u"http://%(url)s/.\n\n- The team of %(site_name)s."), {
                'username': model.username,
                'url': current_site.domain,
                'site_name': settings.SITE_NAME
            })
            send_mail(title, message, settings.DEFAULT_FROM_EMAIL,
                [model], fail_silently=True)

        model.save()

admin.site.register(Profile, ProfileAdmin)
admin.site.unregister(User)
