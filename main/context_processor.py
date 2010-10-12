# -*- coding: utf-8 -*-
# Copyright (C) 2010 Daniel García Moreno <dani AT danigm DOT net>
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

from django.conf import settings
from user.models import Profile
from news.models import New
from django.contrib.auth.forms import AuthenticationForm

def base(request):
    '''
    This is a context processor that adds some vars to the base template
    '''
    if request.method == 'POST' and request.POST.has_key('id_username'):
        login_form = AuthenticationForm(request.POST)
        login_form.is_valid()
    else:
        login_form = AuthenticationForm()
    return {
        'SITE_NAME': settings.SITE_NAME,
        'MEDIA_URL': settings.MEDIA_URL,
        'user': request.user,
        'front_news': New.objects.filter(hidden=False).order_by("-publish_date")[:3],
        'session': request.session,
        'login_form': login_form,
        'current_tab': 'default'
    }
