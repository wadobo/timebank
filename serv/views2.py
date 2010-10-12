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

from serv.models import (Servicio, Zona, Categoria,
                         ContactoIntercambio, MensajeI,
                         ContactoAdministracion, MensajeA)
from serv.forms import ServiceForm, ContactoIForm, MensajeIForm


class MyServices(ViewClass):
    @login_required
    @csrf_protect
    def GET(self):
        user = self.request.user
        created_services = Servicio.objects.filter(creador=user)

        serv_offer = created_services.filter(oferta=True, activo=True)
        serv_request = created_services.filter(oferta=False, activo=True)
        serv_inactive = created_services.filter(activo=False)

        context = dict(serv_offer=serv_offer,
                       serv_request=serv_request,
                       serv_inactive=serv_inactive,
                       current_tab="services",
                       subtab="my-services")
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
            form.save()
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


myservices = MyServices()
add = AddService()
edit = EditService()
delete = DeleteService()
active = ActiveService()
deactive = DeactiveService()
