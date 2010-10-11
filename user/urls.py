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


base_url = '/user/'
remember_sent_url = 'remember/sent/'
remember_complete_url = 'remember/complete/'
password_change_done_url =  'password_change/done/'

urlpatterns = patterns('',
    url(r'^login/$', 'user.views.login', name="user-login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name="user-logout"),
    url(r'^register/$', 'user.views.register', name="user-register"),
    url(r'^%s$' % remember_sent_url, 'user.views.password_reset_done',
        name="user-remember-sent"),
    url(r'^%s$' % remember_complete_url, 'user.views.password_reset_complete',
        name="user-remember-complete"),
    url(r'^profile/$', 'user.views.edit_profile', name="user-edit-profile"),
    url(r'^preferences/$', 'user.views.preferences', name="user-preferences"),
    url(r'^%s$' % password_change_done_url, 'user.views.password_change_done',
        name="user-password-change-done"),
    url(r'^remove/$', 'user.views.remove', name="user-remove"),
    url(r'^view/$', 'user.views.view_profile', name="user-view-current"),
    url(r'^view/(?P<user_id>\d+)/$', 'user.views.view_profile',
        name="user-view"),
)

urlpatterns += patterns('',
    url(r'^remember/$', 'django.contrib.auth.views.password_reset', {
        'template_name': 'user/password_reset.html',
        'email_template_name': 'user/password_reset_email.html',
        'post_reset_redirect': base_url + remember_sent_url},
        name="user-remember"),
    url(r'^remember/confirm/([^/]+)/([^/]+)/$', 
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'user/password_reset_confirm.html',
        'post_reset_redirect': base_url + remember_complete_url},
        name="user-remember-confirm"),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change', {
        'template_name': 'user/password_change.html',
        'post_change_redirect': base_url + password_change_done_url},
        name="user-password-change"),
)
