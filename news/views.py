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

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from utils import ViewClass
from news.models import New
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.conf import settings
from django.http import Http404
from django.core.paginator import Paginator

class NewView(ViewClass):
    def GET(self, new_id):
        new = get_object_or_404(New, pk=new_id)
        if new.hidden:
            raise Http404
        return self.context_response('news/new.html', {'new': new})


class Index(ViewClass):
    def GET(self):
        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        news = New.objects.filter(hidden=False)

        paginator = Paginator(news, 25)
        try:
            news = paginator.page(page)
        except (EmptyPage, InvalidPage):
            news = paginator.page(paginator.num_pages)

        context = dict(news=news)
        return self.context_response('news/list.html', context)


class Feed(ViewClass):
    def GET(self):
        entries = New.objects.filter(hidden=False)[:20]
        current_site = Site.objects.get_current()
        link = "http://%s%s" % (current_site.domain,
            reverse('news.views.index'))
        context = dict(entries=entries,
            title=_("Novedades en %s" % settings.SITE_NAME),
            link=link,
            description=_("Novedades en %s" % settings.SITE_NAME))
        return self.context_response('news/feed.xml', context)


view = NewView()
feed = Feed()
index = Index()
