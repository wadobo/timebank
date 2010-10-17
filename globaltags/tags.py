
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

from django import template
from django.template import RequestContext
from messages.models import Message
import urllib, hashlib

register = template.Library()

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
        return {"transfer": ongoing_transfers[0]}
    else:
        return {"service": service}

@register.filter
def limit_results(objects_list, limit=10):
    if not objects_list:
        return objects_list

    return objects_list[:limit]
