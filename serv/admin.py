# Copyright (C) 2009 Tim Gaggstatter <Tim.Gaggstatter AT gmx DOT net>
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

from serv.models import Service, Area, Category, Transfer
from django.contrib import admin

class ServiceAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    list_display = ('creator', 'short_name', 'is_offer', 'is_active')
    list_filter = ('is_offer','is_active','category', 'area')
    list_display_links = ('creator',)
    search_fields = ['^creator__username', 'description', ]


admin.site.register(Service, ServiceAdmin)
admin.site.register(Area)
admin.site.register(Category)
admin.site.register(Transfer)
