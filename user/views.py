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

from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login as django_login
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator

from datetime import datetime, timedelta

from utils import ViewClass, send_mail_to_admins, login_required
from forms import (RegisterForm, EditProfileForm, RemoveForm,
    PublicMessageForm, FindPeopleForm)
from models import Profile
from messages.models import Message

class Register(ViewClass):
    def GET(self):
        form = RegisterForm()
        return self.context_response('user/register.html', {'form': form,
            'current_tab': 'register'})

    def POST(self):
        form = RegisterForm(self.request.POST)
        if not form.is_valid():
            return self.context_response('user/register.html', {'form': form,
            'current_tab': 'register'})

        # Register user
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        # Send an email to admins and another to the user
        subject = _("[%s] Usuario %s registrado") % (settings.SITE_NAME,
            new_user.username)
        message = _("Se ha registrado un nuevo usuario con nombre de usuario "\
        " %s . Revise sus datos y delo de alta.") % new_user.username
        send_mail_to_admins(subject, message)

        current_site = Site.objects.get_current()
        subject = _("Te has registrado como %s en %s") % (new_user.username,
            settings.SITE_NAME)
        message = _(u"Hola %s!\n Te acabas de registrar en http://%s/."
            u"Próximamente la creación de tu usuario será revisada por"
            u"nuestros administradores y si todo está correcto, activaremos tu"
            u" usuario y podrás comenzar a participar en nuestra comunidad."
            u"\n\n- El Equipo de %s.") %\
            (new_user.username, current_site.domain, settings.SITE_NAME)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
            [new_user.email])

        self.flash(_(u"Te acabas de registrar en nuestro sitio web,"
            u" <strong>%s</strong>. Te hemos enviado un email a"
            u" <strong>%s</strong> confirmándote tu solicitud de inscripción."
            u" Tan pronto como nuestros administradores hayan revisado dicha"
            u" solicitud te avisaremos de nuevo por email y podrás empezar a"
            u" disfrutar de este sistema." % (new_user.username,
                new_user.email)),
            title=_(u"Usuario creado correctamente"))

        return redirect('main.views.index')


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


class PasswordResetDone(ViewClass):
    def GET(self):
        self.flash(_(u"Te hemos enviado un correo a tu dirección de email con"
            u" instrucciones para poder recuperar tu contraseña. Puede tardar"
            u" un poco; se paciente. Si parece que no te llega, comprueba la"
            u" carpeta de correos no deseados."),
            title=_(u"Recuperación de contraseña en proceso"))
        return redirect('main.views.index')


class PasswordResetComplete(ViewClass):
    def GET(self):
        self.flash(_(u"Has cambiado tu contraseña exitosamente, ahora puedes"
            u" entrar introduciendo tu usuario y contraseña en el recuadro"
            u" gris de la izquierda."),
            title=_(u"Contraseña cambiada exitosamente"))
        return redirect('main.views.index')


class EditProfile(ViewClass):
    @login_required
    def GET(self):
        form = EditProfileForm(request=self.request, instance=self.request.user)
        return self.context_response('user/profile.html', {'form': form})

    @login_required
    def POST(self):
        form = EditProfileForm(self.request, self.request.POST,
            instance=self.request.user)
        if not form.is_valid():
            return self.context_response('user/profile.html', {'form': form})

        # Send an email to admins with old data
        old_user = self.request.user
        subject = _("[%s] %s ha modificado sus datos") % (settings.SITE_NAME,
            old_user.username)
        message = _(u"El usuario %s ha modificado su perfil. Datos antiguos:\n\n"
            u" - Nombre: %s\n"
            u" - Apellidos: %s\n"
            u" - Dirección de email: %s\n"
            u" - Dirección física: %s\n"
            u" - Fecha de nacimiento: %s\n"
            u" - Descripción: %s\n\n"
            u"Nuevos datos:\n\n"
            u" - Nombre: %s\n"
            u" - Apellidos: %s\n"
            u" - Dirección de email: %s\n"
            u" - Dirección física: %s\n"
            u" - Fecha de nacimiento: %s\n"
            u" - Descripción: %s\n\n") % (old_user.username, old_user.first_name,
                old_user.last_name, old_user.email, old_user.address,
                old_user.birth_date, old_user.description,
                form.cleaned_data["first_name"], form.cleaned_data["last_name"],
                form.cleaned_data["email"], form.cleaned_data["address"],
                form.cleaned_data["birth_date"],
                form.cleaned_data["description"]
            )
        send_mail_to_admins(subject, message)
        form.save()

        self.flash(_(u"Perfil actualizado: <a href=\"%s\">ver tu perfil</a>.") %
            reverse("user-view-current"))

        return self.context_response('user/profile.html', {'form': form})


class Preferences(ViewClass):
    @login_required
    def GET(self):
        return self.context_response('user/preferences.html',
            {'current_tab': 'user-preferences'})


class PasswordChangeDone(ViewClass):
    @login_required
    def GET(self):
        self.flash(_(u"Contraseña cambiada."))
        return redirect('user-preferences')


class Remove(ViewClass):
    @login_required
    def GET(self):
        form = RemoveForm()
        return self.context_response('user/remove.html', {'form': form})

    @login_required
    def POST(self):
        form = RemoveForm(self.request.POST)
        if not form.is_valid():
            return self.context_response('user/remove.html', {'form': form})

        # TODO: do not remove user, only marks it as inactive
        user = self.request.user
        user.is_active = False
        user.save()

        # Send an email to admins and another to the user
        subject = _("[%s] Usuario %s desactivado") % (settings.SITE_NAME,
            user.username)
        message = _(u"El usuario %s ha solicitado set eliminado del sitio web."
            u"La razón que ha expuesto es:\n\n%s") % (user.username,
            form.cleaned_data["reason"])
        send_mail_to_admins(subject, message)

        current_site = Site.objects.get_current()
        subject = _("Has borrado tu perfil %s de %s") % (user.username,
            settings.SITE_NAME)
        message = _(u"Hola %s!\n Has borrado tu perfil de http://%s/."
            u"Sentimos que hayas decidido dar este paso. Leeremos la razón"
            u" que nos proporcionaste por la cual te has borrado y la tendremos"
            u" en cuenta para mejorar en el futuro."
            u"\n\n- El Equipo de %s.") %\
            (user.username, current_site.domain, settings.SITE_NAME)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        self.flash(_( u"Sentimos que hayas decidido dar este paso. Leeremos la"
            u" razón que nos proporcionaste por la cual te has borrado y la"
            u" tendremos en cuenta para mejorar en el futuro."),
            title=_(u"Usuario borrado"))

        return redirect("user-logout")


class ViewProfile(ViewClass):
    @login_required
    def GET(self, user_id=None):
        user = user_id and get_object_or_404(Profile, id=user_id) or self.request.user

        send_message_form = None
        if self.request.user.is_authenticated():
            send_message_form = PublicMessageForm()

        messages = Message.objects.public_inbox_for(user)

        return self.context_response('user/view.html', {'profile': user,
            'form': send_message_form, 'message_list': messages})


class FindPeople(ViewClass):
    @login_required
    def GET(self):
        form = FindPeopleForm(self.request.GET)

        people = Profile.objects.all()

        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        if form.data.get("username", ''):
            username = form.data["username"]
            people = people.filter(username__contains=username)

        user_status = form.data.get("user_status", '0')
        if user_status != '0':
            if user_status == '1': # today
                last_date = datetime.now() - timedelta(days=1)
            elif user_status == '2': # this week
                last_date = datetime.now() - timedelta(days=7)
            elif user_status == '3': # this month
                last_date = datetime.now() - timedelta(months=1)
            elif user_status == '4': # this year
                last_date = datetime.now() - timedelta(years=1)
            people = people.filter(last_login__gt=last_date)

        paginator = Paginator(people, 10)
        try:
            people = paginator.page(page)
        except (EmptyPage, InvalidPage):
            people = paginator.page(paginator.num_pages)

        context = dict(
            people=people,
            current_tab="people",
            form=form
        )
        return self.context_response('user/find_people.html', context)


class SendMessage(ViewClass):
    @login_required
    def POST(self, recipient_id=None):
        recipient = get_object_or_404(Profile, id=recipient_id)
        form = PublicMessageForm(self.request.POST)
        new_message = form.save(commit=False)
        new_message.sender = self.request.user
        new_message.recipient = recipient
        new_message.is_public = True
        new_message.save()
        self.flash(_(u"Mensaje añadido al perfil público de %s") %\
            recipient.username)
        return redirect("user-view", user_id=recipient_id)

login = Login()
register = Register()
password_reset_done = PasswordResetDone()
password_reset_complete = PasswordResetComplete()
edit_profile = EditProfile()
preferences = Preferences()
password_change_done = PasswordChangeDone()
remove = Remove()
view_profile = ViewProfile()
send_message = SendMessage()
find_people = FindPeople()
