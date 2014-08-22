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


from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from djangoratings.fields import RatingField
from django.db.models import signals

from user.models import Profile
from tbmessages.utils import new_transfer_email

class Area(models.Model):

    name = models.CharField(_("Area"), max_length=40)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Category(models.Model):

    name = models.CharField(_(u"Category"), max_length=45)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _(u"Category")
        verbose_name_plural = _(u"Categories")


OFFER_CHOICES = (
    (True, _('offer')),
    (False, _('demand'))
)

class Service(models.Model):
    creator = models.ForeignKey(Profile, related_name="services",
        verbose_name=_("Creator"))
    is_offer = models.BooleanField(_("Service type"), choices=OFFER_CHOICES)
    pub_date = models.DateTimeField(_(u"Publish date"),
        auto_now=True, auto_now_add=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(_(u"Description"), max_length=400)
    category = models.ForeignKey(Category, verbose_name=_('Category'))
    area = models.ForeignKey(Area, null=True, blank=True,
        verbose_name=_("Area"))

    def __unicode__(self):
        if self.is_offer:
            msj = _("offered")
        else:
            msj = _("demanded")
        msj = unicode(msj)
        return "%d: '%s' %s from %s" % (self.id, self.short_name(), msj, self.creator)

    def short_name(self):
        if len(self.description) < 53:
            return self.description

        return "%s..." % self.description[:50]

    def transfers_count(self):
        return self.transfers.count()

    def sorted_transfers(self):
        return self.transfers.order_by('-request_date')

    def messages_count(self):
        from tbmessages.models import Message
        return Message.objects.filter(service=self).count()

    def messages(self):
        from tbmessages.models import Message
        return Message.objects.filter(service=self)

    def credits_transfered(self):
        ret = self.transfers.filter(status='d').aggregate(models.Sum('credits'))
        return ret['credits__sum'] and ret['credits__sum'] or 0

    def credit_hours_transfered(self):
        credits = self.credits_transfered()
        if credits % 60 == 0:
            return credits/60

        return credits/60.0

    def ongoing_transfers(self, user):
        if self.is_offer:
            return Transfer.objects.filter(credits_debtor=user, service=self,
                status__in=["q", "a"])
        else:
            return Transfer.objects.filter(credits_payee=user, service=self,
                status__in=["q", "a"])

    class Meta:
        ordering = ('-pub_date', )


TRANSFER_STATUS = (
    ('q', _('requested')), # q for reQuest
    ('a', _('accepted')), # a for Accepted
    ('r', _('cancelled')), # r for Rejected TODO: (but it actually should be c for cancelled)
    ('d', _('done')), # d for Done
)

class Transfer(models.Model):
    rating = RatingField(range=5, allow_anonymous=False, can_change_vote=True)

    def int_rating(self):
        return int(self.rating.score / self.rating.votes)

    # will only be set and used when transfer is not associated with a service
    direct_transfer_creator = models.ForeignKey(Profile,
        related_name='direct_transfers_created', null=True, blank=True,
        verbose_name=_("Direct transfer creator"))

    # Person receiving the credits (and giving the service)
    credits_payee = models.ForeignKey(Profile, related_name='transfers_received',
        verbose_name=_("Credits payee"))

    # Person giving the credits (and receiving the service)
    credits_debtor = models.ForeignKey(Profile, related_name='transfers_given',
        verbose_name=_("Credits debtor"))

    service = models.ForeignKey(Service, related_name='transfers', null=True,
        blank=True, verbose_name=_("Service"))

    # Small description for the received service
    description = models.TextField(_(u"Description"), max_length=300)

    request_date = models.DateTimeField(_("Transfer request date"),
        auto_now=True, auto_now_add=True)

    confirmation_date = models.DateTimeField(_(u"Transfer confirmation date"),
        null=True)

    status = models.CharField(_(u"Status"), max_length=1, choices=TRANSFER_STATUS)

    is_public = models.BooleanField(_(u"Is public"), default=False)

    # credits in minutes
    credits = models.PositiveIntegerField(_(u"Credits"))

    def credit_hours(self):
        return self.credits/60.0

    class meta:
        ordering = ['-request_date']

    def creator(self):
        '''
        Transfer creator
        '''
        if self.service:
            return self.service.creator == self.credits_debtor and\
                self.credits_payee or self.credits_debtor
        else:
            return self.direct_transfer_creator

    def recipient(self):
        '''
        the user which is not the creator
        '''
        if self.service:
            return self.service.creator != self.credits_debtor and\
                self.credits_payee or self.credits_debtor
        else:
            return self.direct_transfer_creator == self.credits_debtor and\
                self.credits_payee or self.credits_debtor

    def is_direct(self):
        return not self.service

    def status_readable(self):
        return TRANSFER_STATUS[self.status]

    def __unicode__(self):
        return self.description[0:53] + '...'

signals.post_save.connect(new_transfer_email, sender=Transfer)
