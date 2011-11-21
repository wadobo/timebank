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
from django.utils.translation import ugettext as _
from datetime import datetime


def apply_transfer(modeladmin, request, queryset):
    for transfer in queryset:
        transfer.status = "d"
        transfer.confirmation_date = datetime.now()
        transfer.credits_debtor.balance -= transfer.credits
        transfer.credits_payee.balance += transfer.credits
        transfer.credits_debtor.save()
        transfer.credits_payee.save()
        transfer.save()
apply_transfer.short_description = _("Apply tranfer")

class ServiceAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    list_display = ('creator', 'short_name', 'is_offer', 'is_active')
    list_filter = ('is_offer','is_active','category', 'area')
    list_display_links = ('creator',)
    search_fields = ['^creator__username', 'description', ]


class TransferAdmin(admin.ModelAdmin):
    date_hierarchy = 'request_date'
    list_display = ('service', 'credits', 'credits_payee',
                    'credits_debtor', 'status', 'request_date', 'confirmation_date')
    list_filter = ('status', )
    list_display_links = ('service',)
    search_fields = ['^service__category', 'description', ]

    actions = [apply_transfer]


admin.site.register(Service, ServiceAdmin)
admin.site.register(Area)
admin.site.register(Category)
admin.site.register(Transfer, TransferAdmin)
