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

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = patterns('main.views',
    url(r'^contact/$', 'contact', name="contact"),
    url(r'^set_language/$', 'set_language', name="set_language"),
    url(r'^report1.csv$', 'report1', name="report1"),
    url(r'^report2.csv$', 'report2', name="report2"),
    url(r'^report3.csv$', 'report3', name="report3"),
    url(r'^report4.csv$', 'report4', name="report4"),
    url(r'^report5.csv$', 'report5', name="report5"),
    (r'^/?$', 'index'),
    (r'^robots\.txt$', TemplateView.as_view(template_name="robots.txt",
                                            content_type='text/plain')),
)
