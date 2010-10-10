# -*- coding: utf-8 -*- 
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

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    #(r'^$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    #(r'^user/register/$', 'aplicacion.views.register'),
    #(r'^user/registerdone/$', 'django.views.generic.simple.direct_to_template',
        #{'template': 'registerdone.html',
        #'extra_context': {"SITE_NAME": settings.SITE_NAME}}
    #),
    #(r'^personal/$', 'aplicacion.views.personal'),#django.views.generic.create_update.update_object
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', #Para servir archivos estáticos
        {'document_root': settings.STATIC_DOC_ROOT, 'show_indexes': True}),
    #(r'^publico/(?P<id_usu>[0-9]*)$', 'aplicacion.views.publico'),
    #(r'^servicios/$', 'serv.views.misservicios'),
    #(r'^buscador/$', 'serv.views.buscador'),
    #(r'^mensajes/$', 'serv.views.mensajesTransf'),
    #(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    #(r'^personal/cambiopwd/$', 'aplicacion.views.cambioPwd'),
    #(r'^personal/cambiopwd/hecho$', 'aplicacion.views.pwdCambiado'),
    #(r'^personal/baja$', 'aplicacion.views.baja'),
    #(r'^publico/comentar/(?P<id_usu>[0-9]*)$', 'aplicacion.views.comentar'),
    #(r'^contactar/$', 'serv.views.contactar'),
    #(r'^mensajes/intercambio/(?P<id_inter>[0-9]+)$', 'serv.views.intercambio'),
    #(r'^mensajes/transferencia/$', 'aplicacion.views.transferencia'),
    #(r'^personal/contactoadmin/$', 'serv.views.contAdm'),
    #(r'^personal/mensajesadmin/$', 'serv.views.msjAdm'),
    #(r'^probando/$', 'serv.views.buscador'),
    #(r'^recordar/$', 'aplicacion.views.recuerdoClave'),
    ## (r'^databrowse/(.*)', databrowse.site.root),
    #(r'^dummy-mail/$', 'aplicacion.views.dummy_mail'),
    (r'^user/', include('user.urls')),
    (r'^news/', include('news.urls')),
    (r'^messages/', include('messages.urls')),
    (r'^services/', include('serv.urls')),
    (r'^', include('main.urls')),
)

