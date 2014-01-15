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

from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('news.views',
    url(r'^$', 'index', name="news"),
    url(r'^view/(\d+)$', 'view', name="news-view"),
    url(r'^feed$', 'feed', name="news-feed"),
)

