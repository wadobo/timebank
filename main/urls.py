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

urlpatterns = patterns('main.views',
    url(r'^contact/$', 'contact', name="contact"),
    (r'^/?$', 'index'),
)

urlpatterns += patterns('django.views.generic.simple',
    url(r'^faq/$', 'direct_to_template', {'template': 'static/faq.html'}, name="static-faq"),
    url(r'^tos/$', 'direct_to_template', {'template': 'static/tos.html'}, name="static-tos"),
    url(r'^dev/$', 'direct_to_template', {'template': 'static/dev.html'}, name="static-dev"),
    url(r'^about/$', 'direct_to_template', {'template': 'static/about.html'}, name="static-about"),
)

