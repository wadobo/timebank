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

from aplicacion.models import PerfilUsuario, Comentario, Transferencia
from django.contrib.auth.models import User, Message, Group
from django.contrib import admin
admin.site.unregister(User)
admin.site.unregister(Group)

class TransferenciaAdmin(admin.ModelAdmin):
    date_hierarchy = 'fechaTx'
    list_display = ('beneficiario','deudor','descrServ','fechaTx','cantidad','rechazada','realizada')
    list_filter = ('rechazada','realizada',)
    list_display_links = ('beneficiario','deudor','descrServ',)
    search_fields = ['^beneficiario__username', '^deudor__username', 'descrServ']

class PerfilInline(admin.StackedInline):
    model = PerfilUsuario

class UsuarioAdmin(admin.ModelAdmin):
    inlines = [
        PerfilInline,
    ]
    fieldsets = (
        ('Datos personales', {
            'fields': ('first_name', 'last_name', 'email', 'is_active')
        }),
        ('Opciones avanzadas', {
            'classes': ('collapse',),
            'fields': ('username','is_staff', 'is_superuser', 'date_joined', 'last_login',)
        }),
    )
    date_hierarchy = 'date_joined'
    list_display = ('username','date_joined','first_name','last_name','email',)
    list_filter = ('is_active','is_staff',)
    list_display_links = ('username',)
    search_fields = ['^username', '^first_name', '^last_name']
    list_per_page = 40

    def save_model(self, request, model, form, change):
        current_model = 

class ComentarioAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    list_display = ('autor','destinatario','contenidoCorto','puntuacion','pub_date',)
    list_display_links = ('autor','destinatario',)
    search_fields = ['^autor__username', '^destinatario__username', 'contenido']
    list_per_page = 60

admin.site.register(Message)
admin.site.register(User, UsuarioAdmin)
#admin.site.register(PerfilUsuario)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(Transferencia, TransferenciaAdmin)
