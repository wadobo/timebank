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
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import signals

from utils import ViewClass, send_mail_to_admins, login_required
from forms import AnonymousContactForm, ContactForm
from serv.models import Servicio
from messages.utils import new_transfer_email

class Migrate(ViewClass):
    @login_required
    def GET(self):
        if not self.request.user.is_superuser:
            self.flash(_(u'No tienes permisos'), 'error')
            redirect('main.views.index')
        from user.models import Profile
        from aplicacion.models import PerfilUsuario, Transferencia
        from serv.models import Transfer

        # Migrate profiles
        perfiles = PerfilUsuario.objects.all()
        for perfil in perfiles:
            profile = Profile()
            profile.__dict__.update(perfil.user.__dict__)
            profile.birth_date = perfil.fecha_de_nacimiento
            profile.address = perfil.direccion
            profile.description = perfil.descr
            profile.balance = int(float(perfil.saldo)*60)
            profile.save()

        # Migrate transfers
        transferencias = Transferencia.objects.all()
        # disable sending emails during migration
        signals.post_save.disconnect(new_transfer_email, sender=Transfer)
        for transferencia in transferencias:
            transfer = Transfer()
            if transferencia.creoBeneficiario:
                transfer.direct_transfer_creator_id = transferencia.beneficiario_id
            else:
                transfer.direct_transfer_creator_id = transferencia.deudor_id
            transfer.credits_payee_id = transferencia.beneficiario_id
            transfer.credits_debtor_id = transferencia.deudor_id
            transfer.description = transferencia.descrServ
            transfer.request_date = transferencia.fechaTx
            if transferencia.realizada and not transferencia.rechazada:
                transfer.confirmation_date = transferencia.fechaTx
            if transferencia.realizada:
                transfer.status = 'd'
            elif transferencia.rechazada:
                transfer.status = 'r'
            else:
                transfer.status = 'q'
            transfer.is_public = False
            transfer.credits = int(float(transferencia.cantidad)*60)
            transfer.save()
        signals.post_save.connect(new_transfer_email, sender=Transfer)

        self.flash(_(u'Migración realizada'))
        return redirect('main.views.index')

class Index(ViewClass):
    def GET(self):
        services = Servicio.objects.filter(activo=True)
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
            subject = _("[%(site_name)s] %(username)s: %(email_subject)s") % {
                'site_name': settings.SITE_NAME,
                'username': user.username,
                'subject': form.cleaned_data["subject"]
            }
            message = _(u"El usuario registrado %(username)s llamado envía "\
            " el siguiente mensaje:\n%(message)s") % {
                'username': user.username,
                'message': form.cleaned_data["message"]
            }
        else:
            subject = _("[%(site_name)s] %(email)s: %(email_subject)s") % {
                'site_name': settings.SITE_NAME,
                'email': form.cleaned_data["email"],
                'subject': form.cleaned_data["subject"]
            }
            message = _("El usuario no registrado %(name)s cuyo email es %(email)s"\
                "envía el siguiente mensaje:\n%(message)s") % {
                    'name': form.cleaned_data["name"],
                    'email': form.cleaned_data["email"],
                    'message': form.cleaned_data["message"]
                }
        send_mail_to_admins(subject, message)

        self.flash(_("Mensaje enviado, te responderemos lo antes posible"))
        return redirect('main.views.index')

index = Index()
contact = Contact()
migrate = Migrate()
