# -*- coding: utf-8 -*-
# Copyright (C) 2010 Daniel Garcia Moreno <dani@danigm.net>
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

from utils import ViewClass

from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.http import Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from serv.models import (Servicio, Zona, Categoria,
                         ContactoIntercambio, MensajeI,
                         ContactoAdministracion, MensajeA, Transfer)
from serv.forms import (ServiceForm, ContactoIForm, MensajeIForm,
    ListServicesForm, AddTransferForm)
from user.models import Profile


class ListServices(ViewClass):
    @login_required
    def GET(self):
        form = ListServicesForm(self.request.GET)

        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        if form.data.get("mine", ''):
            services = Servicio.objects.filter(creador=self.request.user)
            subtab = "my"
        else:
            services = Servicio.objects.filter(activo=True)
            subtab = "find"

        if form.data.get("the_type", '') == "1":
            services = services.filter(oferta=True)
        elif form.data.get("the_type", '') == "2":
            services = services.filter(oferta=False)

        if form.data.get("category", ''):
            category = get_object_or_404(Categoria, id=int(form.data["category"]))
            services = services.filter(categoria=category)

        if form.data.get("area", ''):
            area = get_object_or_404(Zona,
                id=int(form.data["area"]))
            services = services.filter(zona=area)

        if form.data.get("username", ''):
            username = form.data["username"]
            services = services.filter(creador__username__contains=username)

        paginator = Paginator(services, 25)
        try:
            services = paginator.page(page)
        except (EmptyPage, InvalidPage):
            services = paginator.page(paginator.num_pages)

        context = dict(
            services=services,
            current_tab="services",
            subtab=subtab,
            form=form
        )
        return self.context_response('serv/services.html', context)


class AddService(ViewClass):
    @login_required
    @csrf_protect
    def GET(self):
        form = ServiceForm()
        context = dict(form=form, instance=None, current_tab="services",
            subtab="add")
        return self.context_response('serv/edit_service.html', context)

    @login_required
    @csrf_protect
    def POST(self):
        form = ServiceForm(self.request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.creador = self.request.user
            service.save()
            self.flash(_(u"Servicio añadido correctamente"))
            return redirect('serv-myservices')
        context = dict(form=form, instance=None, current_tab="services",
            subtab="add")
        return self.context_response('serv/edit_service.html', context)


class EditService(ViewClass):
    @login_required
    @csrf_protect
    def GET(self, sid):
        instance = get_object_or_404(Servicio, pk=sid)
        if not instance.creador == self.request.user:
            self.flash(_(u"No puedes modificar un servicio que no es tuyo"),
                       "error")
            return redirect('serv-myservices')
        form = ServiceForm(instance=instance)
        context = dict(form=form, instance=instance, current_tab="services",
            subtab="my-services")
        return self.context_response('serv/edit_service.html', context)

    @login_required
    @csrf_protect
    def POST(self, sid):
        instance = get_object_or_404(Servicio, pk=sid)
        if not instance.creador == self.request.user:
            self.flash(_(u"No puedes modificar un servicio que no es tuyo"),
                       "error")
            return redirect('serv-myservices')
        form = ServiceForm(self.request.POST, instance=instance)

        if form.is_valid():
            current_is_offer = instance.oferta
            service = form.save(commit=False)

            # If there are ongoing transfers, oferta field cannot be changed or
            # else havoc will follow:
            if Transfer.objects.filter(service=instance,
                status__in=["q", "a"]).count() > 0 and\
                service.oferta != current_is_offer:
                self.flash(_(u"No puedes cambiar el servicio de oferta a demanda"
                    " mientras hay transferencias en curso"), "error")
                return redirect('serv-myservices')
            service.save()
            self.flash(_(u"Servicio modificado correctamente"))
            return redirect('serv-myservices')
        context = dict(form=form, instance=instance, current_tab="services",
            subtab="my-services")
        return self.context_response('serv/edit_service.html', context)


class DeleteService(ViewClass):
    @login_required
    @csrf_protect
    def POST(self, sid):
        instance = get_object_or_404(Servicio, pk=sid)
        if instance.creador == self.request.user:
            instance.delete()
            self.flash(_(u"Servicio eliminado correctamente"))
        else:
            self.flash(_(u"No puedes eliminar un servicio que no es tuyo"),
                       "error")
        return redirect('serv-myservices')


class ActiveService(ViewClass):
    @login_required
    @csrf_protect
    def POST(self, sid):
        instance = get_object_or_404(Servicio, pk=sid)
        if instance.creador == self.request.user:
            instance.activo = True
            instance.save()
            self.flash(_(u"Servicio activado correctamente"))
        else:
            self.flash(_(u"No puedes modificar un servicio que no es tuyo"),
                       "error")
        return redirect('serv-myservices')


class DeactiveService(ViewClass):
    @login_required
    @csrf_protect
    def POST(self, sid):
        instance = get_object_or_404(Servicio, pk=sid)
        if instance.creador == self.request.user:
            instance.activo = False
            instance.save()
            self.flash(_(u"Servicio desactivado correctamente"))
        else:
            self.flash(_(u"No puedes modificar un servicio que no es tuyo"),
                       "error")
        return redirect('serv-myservices')


class AddTransfer(ViewClass):
    @login_required
    @csrf_protect
    def GET(self, service_id):
        service = get_object_or_404(Servicio, pk=service_id)
        form = AddTransferForm()
        context = dict(form=form, current_tab="transfers", subtab="add",
            service=service)
        return self.context_response('serv/add_transfer.html', context)

    @login_required
    @csrf_protect
    def POST(self, service_id):
        service = get_object_or_404(Servicio, pk=service_id)
        form = AddTransferForm(data=self.request.POST)
        # Check user would not surpass min balance
        if self.request.user.balance < settings.MIN_CREDIT and\
            service.oferta:
            self.flash(_(u"No tienes suficiente crédito"), 'error')
            return redirect('/')

        if service.creador == self.request.user:
            self.flash(_(u"No puedes solicitarte un servicio a tí mismo"))
            return redirect('/')

        if form.is_valid():
            transfer = form.save(commit=False)
            # Set remaining transfer settings
            transfer.service = service
            transfer.status = 'q'
            if transfer.service.oferta:
                transfer.credits_debtor = self.request.user
                transfer.credits_payee = transfer.service.creador
            else:
                transfer.credits_payee = self.request.user
                transfer.credits_debtor = transfer.service.creador

            # Check user would not surpass max balance
            if transfer.credits_payee.balance + transfer.credits > settings.MAX_CREDIT:
                self.flash(_(u"La transferencia superaría el límite de"
                    u" crédito del receptor de créditos"), 'error')
                return redirect('/')

            # Check user would not minimum min balance
            if transfer.credits_debtor.balance - transfer.credits < settings.MIN_CREDIT:
                self.flash(_(u"La transferencia superaría el límite mínimo "
                    u"de crédito de la persona que recibiría el servicio"),
                    'error')
                return redirect('/')

            # Check there's no current ongoing transfer for this service and
            # self.request.user
            if Transfer.objects.filter(credits_payee=transfer.credits_payee,
                credits_debtor=transfer.credits_debtor,
                service=service, status__in=['q', 'a']).count() > 0:
                self.flash(_(u"Ya tienes una transferencia en curso para"
                    u" este servicio"),'error')
                return redirect('/')

            transfer.save()
            self.flash(_(u"Transferencia creada correctamente"))
            return redirect('/') #TODO transfers-list-mine

        context = dict(form=form, instance=None, current_tab="transfers",
            subtab="add", service=service)
        return self.context_response('serv/add_transfer.html', context)


class EditTransfer(ViewClass):
    @login_required
    @csrf_protect
    def GET(self, transfer_id):
        transfer = get_object_or_404(Transfer, pk=transfer_id)
        if transfer.creator() != self.request.user:
            self.flash(_(u"No puedes modificar una transferencia que no sea tuya"),
                "error")
            return redirect('/')
        if transfer.status != "q":
            self.flash(_(u"Sólo se pueden modificar transferencias aun no aceptadas"),
                "error")
            return redirect('/')
        form = AddTransferForm(instance=transfer)
        context = dict(form=form, transfer=transfer, current_tab="transfers",
            subtab="mine")
        return self.context_response('serv/edit_transfer.html', context)

    @login_required
    @csrf_protect
    def POST(self, transfer_id):
        transfer = get_object_or_404(Transfer, pk=transfer_id)
        if transfer.creator() != self.request.user:
            self.flash(_(u"No puedes modificar una transferencia que no sea"
                " tuya"), "error")
            return redirect('/')
        if transfer.status != "q":
            self.flash(_(u"Sólo se pueden modificar transferencias aun no"
                " aceptadas"), "error")
            return redirect('/')

        form = AddTransferForm(self.request.POST, instance=transfer)
        if form.is_valid():
            transfer = form.save(commit=False)
            # Check user would not surpass max balance
            if transfer.credits_payee.balance + transfer.credits > settings.MAX_CREDIT:
                self.flash(_(u"La transferencia superaría el límite de"
                    u" crédito del receptor de créditos"), 'error')
                return redirect('/')

            # Check user would not minimum min balance
            if transfer.credits_debtor.balance - transfer.credits < settings.MIN_CREDIT:
                self.flash(_(u"La transferencia superaría el límite mínimo "
                    u"de crédito de la persona que recibiría el servicio"),
                    'error')
                return redirect('/')

            transfer.save()
            self.flash(_(u"Transferencia modificada correctamente"))
            return redirect('/')
        context = dict(form=form, transfer=transfer, current_tab="transfer",
            subtab="mine")
        return self.context_response('serv/edit_transfer.html', context)

list_services = ListServices()
add = AddService()
edit = EditService()
delete = DeleteService()
active = ActiveService()
deactive = DeactiveService()
add_transfer = AddTransfer()
edit_transfer = EditTransfer()
