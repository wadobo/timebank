
# -*- coding: utf-8 -*-
# Django settings for timebank project.
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

import os
from PIL import Image
from django import template
from django.template import RequestContext
import urllib, hashlib
from django.conf import settings

from djangoratings.templatetags.ratings import *
from messages.models import Message
from user.models import Profile

register = template.Library()

@register.simple_tag
def avatar(user, size=48):
    puser = Profile.objects.get(username=user.username)
    if(puser.photo):
        path = puser.photo.path
        path = "%s_%s.png" % (path, size)
        if not os.path.exists(path):
            im = Image.open(puser.photo.path)
            im.thumbnail((size, size))
            im.save(path)

        path = path[len(settings.STATIC_DOC_ROOT) + 1:]
        return settings.STATIC_URL + path
    else:
        return gravatar(user.email, size)

@register.simple_tag
def gravatar(email, size=48, d='identicon'):
    gravatar_url = "http://www.gravatar.com/avatar.php?"
    gravatar_url += urllib.urlencode({
        'gravatar_id': hashlib.md5(email.lower()).hexdigest(),
        'size': str(size),
        'd': d})
    return gravatar_url

@register.filter
def truncate_chars(string, max_pos=75, ellipsis=True):
    if ellipsis:
        suffix = '...'
    else:
        suffix = ''
    length = len(string)
    if length >= max_pos:
        return string[:max_pos] + suffix
    else:
        return string

# Even if this is a "simple tag", we need to create an inclusion_tag because
# those are the only ones with context support at the moment
@register.inclusion_tag("main/simple_context_tag.html",\
    takes_context=True)
def num_unread_messages(context):
    user = context['user']
    unread_messages_count = Message.objects.inbox_for(user)\
        .filter(read_at__isnull=True).count()
    value = "<small>%s</small>" % unread_messages_count
    return {"value": value}

@register.inclusion_tag("main/simple_context_tag.html",\
    takes_context=True)
def current_tab(context, tab, var="current_tab"):
    '''
    Prints "current" if current_tab context var is the one given
    '''
    if context.has_key(var) and context[var] == tab:
        return {"value": "current"}
    else:
        return {"value": ""}

@register.inclusion_tag("serv/service_transfer_actions.html",\
    takes_context=True)
def transfer_actions(context, service):
    '''
    Renders actions for a given service if any. Assumes user is authenticated
    '''
    ongoing_transfers = service.ongoing_transfers(context["user"])
    if ongoing_transfers:
        return {"transfer": ongoing_transfers[0], 'user': context["user"]}
    else:
        return {"service": service}

@register.filter
def limit_results(objects_list, limit=10):
    if not objects_list:
        return objects_list

    return objects_list[:limit]

register.tag('rating_by_user', do_rating_by_user)

@register.inclusion_tag("serv/transfer_rating.html",\
    takes_context=True)
def transfer_rating(context, transfer):
    '''
    Renders actions for a given service if any. Assumes user is authenticated
    '''
    return {"transfer": transfer, "user": context["user"]}

@register.inclusion_tag("user/user_rating.html",\
    takes_context=True)
def user_rating(context, user):
    '''
    Renders actions for a given service if any. Assumes user is authenticated
    '''
    return {"user": user}
