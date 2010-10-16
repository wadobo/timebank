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

from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from views2 import (list_services, view, add, edit, delete, active, deactive,
    add_transfer, edit_transfer, cancel_transfer)

urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url': 'list/?mine=true'}, name="serv-myservices"),
    url(r'^list/.*$', list_services, name='serv-list'),
    url(r'^add/$', add, name='serv-add'),
    url(r'^edit/(\d+)/$', edit, name='serv-edit'),
    url(r'^view/(\d+)/$', view, name='serv-view'),
    url(r'^delete/(\d+)/$', delete, name='serv-del'),
    url(r'^active/(\d+)/$', active, name='serv-active'),
    url(r'^deactive/(\d+)/$', deactive, name='serv-deactive'),
    url(r'^transfer/add/(\d+)/$', add_transfer, name='serv-transfer-add'),
    url(r'^transfer/edit/(\d+)/$', edit_transfer, name='serv-transfer-edit'),
    url(r'^transfer/cancel/(\d+)/$', cancel_transfer, name='serv-transfer-cancel'),
    #url(r'^talk/(\d+)/$', talk, name='serv-talk'),
)
