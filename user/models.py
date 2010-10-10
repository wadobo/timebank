# -*- coding: utf-8 -*- 
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

from django.contrib.auth.models import User, UserManager
from django.utils.translation import ugettext as _
from django.db import models
from django.db.models import signals
from datetime import date

def create_profile_for_user(sender, **kwargs):
    '''
    This way everytime a User is created, a Profile is created too.
    '''
    if kwargs['created']:
        profile = Profile()
        profile.birth_date = date.today()
        profile.address = _(u"dirección")
        profile.__dict__.update(kwargs['instance'].__dict__)
        profile.save()

signals.post_save.connect(create_profile_for_user, sender=User)

class Profile(User):
    '''
    User with time bank settings.
    '''
    birth_date = models.DateField(_(u"Fecha de Nacimiento"))

    address = models.CharField(_(u"Dirección"), max_length=100)

    balance = models.IntegerField(default=0)

    description = models.TextField(_(u"Descripción personal"), max_length=300,
        blank=True)

    karma = models.CommaSeparatedIntegerField(_("Karma"), default=0,
        max_length=4)
    
    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")

    def __unicode__(self):
        return _("Id: %s usuario: %s") % (self.id, self.username)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager() 

    def __eq__(self, value):
        return self.id == value.id
