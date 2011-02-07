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


from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site


class New(models.Model):

    title = models.CharField(_(u"Title"), max_length=300, blank=True)
    creation_date = models.DateTimeField(_(u"Creation date"),
        auto_now=True)
    last_modified_date = models.DateTimeField(_(u"Last modification date"),
        auto_now=True)
    publish_date = models.DateTimeField(_(u"Publish date"),
        auto_now=True)
    hidden = models.BooleanField(_(u"Hidden"), default=False)
    body = models.TextField(_(u"Body"))
    author = models.ForeignKey(User, verbose_name=_("User"))
    author.verbose_name = _(u"Author")

    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")
        
    def __unicode__(self):
        return self.title

    def get_url(self):
        current_site = Site.objects.get_current()
        link = "http://%s%s" % (current_site.domain,
                                reverse('news.views.view', args=(self.id, )))
        return link
