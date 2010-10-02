# Copyright (C) 2009 Tim Gaggstatter <Tim.Gaggstatter AT gmx DOT net>
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

from serv.models import Servicio, Zona, Categoria, ContactoAdministracion, ContactoIntercambio, MensajeA, MensajeI
from django.contrib import admin

class ServicioAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    list_display = ('creador','cortaServicio','oferta','activo',)
    list_filter = ('oferta','activo','categoria', 'zona')
    list_display_links = ('creador',)
    search_fields = ['^creador__username', 'descripcion', ]

class MensajesAdmInline(admin.TabularInline):
    model = MensajeA

class ContactoAdmAdmin(admin.ModelAdmin):
    inlines = [
        MensajesAdmInline,
    ]
    list_display = ('administrador','usuario_normal','tema',)
    list_filter = ('usuario_borrar','administrador_borrar',)
    list_display_links = ('administrador','usuario_normal','tema',)
    search_fields = ['^administrador__username', '^usuario_normal__username','tema', ]
    list_per_page = 40

class MensajesIntInline(admin.TabularInline):
    model = MensajeI

class ContactoIntAdmin(admin.ModelAdmin):
    inlines = [
        MensajesIntInline,
    ]
    fields = ('oferente','solicitante','oferente_borrar','solicitante_borrar',)
    list_display = ('oferente','solicitante','descripcion_del_servicio',)#,'resumenTema'
    list_filter = ('oferente_borrar','solicitante_borrar',)
    list_display_links = ('oferente','solicitante',)#'resumenTema',
    search_fields = ['^oferente__username', '^solicitante__username','servicio__descripcion']
    list_per_page = 40

class MensajesAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    search_fields = ['contenido', ]
    list_per_page = 200
	
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(Zona)
admin.site.register(Categoria)
admin.site.register(ContactoIntercambio, ContactoIntAdmin)
admin.site.register(ContactoAdministracion, ContactoAdmAdmin)
admin.site.register(MensajeI, MensajesAdmin)
admin.site.register(MensajeA, MensajesAdmin)
