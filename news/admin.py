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


from django.contrib import admin
from news.models import New
from django.db import models
from tinymce.widgets import AdminTinyMCE


class NewsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE},
    }
    exclude = ('author', )
    list_display = ('title', 'publish_date', 'hidden', 'author')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()

admin.site.register(New, NewsAdmin)
