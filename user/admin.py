from django.contrib.auth.admin import UserAdmin
from models import Profile
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

class ExtraProfileInline(admin.StackedInline):
    model = Profile
    fieldsets = (('Datos Extra', {
        'fields': ('birth_date', 'address', 'balance')
    }),)
    list_display = ('birth_date', 'address', 'balance')

class ProfileAdmin(UserAdmin):
    inlines = [
        ExtraProfileInline,
    ]

admin.site.register(Profile, ProfileAdmin)
admin.site.unregister(User)
