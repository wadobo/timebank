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

    title = models.CharField(_(u"Título"), max_length=300, blank=True)
    published = models.DateTimeField(_(u"Fecha de publicación"),
                                     auto_now=True)
    body = models.TextField(_(u"Cuerpo de la noticia"))
    author = models.ForeignKey(User)
    author.verbose_name = _(u"Autor")

    class Meta:
        verbose_name = _("Noticia")
        verbose_name_plural = _("Noticias")
        
    def __unicode__(self):
        return self.title

    def get_url(self):
        current_site = Site.objects.get_current()
        link = "http://%s%s" % (current_site.domain,
                                reverse('news.views.view', args=(self.id, )))
        return link
