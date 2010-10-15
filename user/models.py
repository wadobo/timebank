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

    # credits in minutes
    balance = models.IntegerField(default=0)

    description = models.TextField(_(u"Descripción personal"), max_length=300,
        blank=True)

    karma = models.CommaSeparatedIntegerField(_("Karma"), default=0,
        max_length=4)

    land_line = models.CharField(_(u"Teléfono fijo"), max_length=20)

    mobile_tlf = models.CharField(_(u"Teléfono móvil"), max_length=20)

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")

    def __unicode__(self):
        return _("Id: %s usuario: %s") % (self.id, self.username)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager() 

    def __eq__(self, value):
        return self.id == value.id


TRANSFER_STATUS = (
    ('q', _('Transferencia solicitada')), # q for reQuest
    ('r', _('Transferencia rechazada')), # r for Rejected
    ('d', _('Transferencia realizada')), # d for Done
)

class Transfer(models.Model):
    # Person receiving the credits (and giving the service)
    credits_payee = models.ForeignKey(Profile, related_name="credits_payee",
        verbose_name=_("Benefeciario"))

    # Person giving the credits (and receiving the service)
    credits_debtor = models.ForeignKey(Profile, related_name="credits_debtor",
        verbose_name=_("Deudor"))

    request_date = models.DateTimeField(_("Fecha de solicitud de transferencia"), auto_now=True,
        auto_now_add=True)

    confirmation_date = models.DateTimeField(_(u"Fecha de confirmación de"
        " transferencia"))

    status = models.CharField(_(u"Estado"), max_length=1, choices=TRANSFER_STATUS)

    # credits in minutes
    credits = models.PositiveIntegerField(_(u"Créditos"))

    #TODO: Add here a rating of the service, set by the payee of course

    class meta:
        ordering = ['-request_date']

