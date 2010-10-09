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

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^login/$', 'user.views.login', name="user-login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': 'main/index.html'}, name="user-logout"),
    url(r'^register/$', 'user.views.register', name="user-register"),
    url(r'^remember/$', 'django.contrib.auth.views.password_reset', {
        'template_name': 'user/password_reset.html',
        'email_template_name': 'user/password_reset_email.html'},
        name="user-remember"),
    url(r'^remember/sent/$', 'django.contrib.auth.views.password_reset_done',
        {'template_name': 'user/password_reset_done.html'},
        name="user-remember-sent"),
    url(r'^remember/confirm/([^/]+)/([^/]+)/$', 
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'user/password_reset_confirm.html'},
        name="user-remember-confirm"),
    url(r'^remember/complete/$',
        'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'user/password_reset_complete.html'},
        name="user-remember-complete"),
)
