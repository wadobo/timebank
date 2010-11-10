

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
from django.utils.translation import ugettext as _
from djangoratings.fields import RatingField
from django.db.models import signals

from user.models import Profile
from messages.utils import new_transfer_email

class Zona(models.Model):

    nombre_zona = models.CharField(max_length=40)

    def __unicode__(self):
        return self.nombre_zona


class Categoria(models.Model):

    nombre_categoria = models.CharField("Categoría", max_length=45)

    def __unicode__(self):
        return self.nombre_categoria

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"


class Servicio(models.Model):

    creador = models.ForeignKey(Profile, related_name="creador")
    #Si es una oferta=true, si es demanda=false
    oferta = models.BooleanField()
    pub_date = models.DateTimeField("Fecha de publicación",
                                    auto_now=True,
                                    auto_now_add=True)
    activo = models.BooleanField(default=True)
    descripcion = models.TextField("Descripción", max_length=400)
    categoria = models.ForeignKey(Categoria)
    zona = models.ForeignKey(Zona)

    def __unicode__(self):
        if self.oferta:
            msj = "ofertado"
        else:
            msj = "solicitado"
        return "Servicio %s %s por: %s" % (self.id, msj, self.creador)

    def cortaServicio(self):
        return "%s..." % self.descripcion[:50]

    def transfers_count(self):
        return self.transfers.count()

    def sorted_transfers(self):
        return self.transfers.order_by('-request_date')

    def messages_count(self):
        from messages.models import Message
        return Message.objects.filter(service=self).count()

    def messages(self):
        from messages.models import Message
        return Message.objects.filter(service=self)

    def credits_transfered(self):
        ret = self.transfers.filter(status='d').aggregate(models.Sum('credits'))
        return ret['credits__sum'] and ret['credits__sum'] or 0

    def ongoing_transfers(self, user):
        if self.oferta:
            return Transfer.objects.filter(credits_debtor=user, service=self,
                status__in=["q", "a"])
        else:
            return Transfer.objects.filter(credits_payee=user, service=self,
                status__in=["q", "a"])

    class Meta:
        ordering = ('-pub_date', )


class ContactoIntercambio(models.Model):

    oferente = models.ForeignKey(User, related_name="oferente")
    solicitante = models.ForeignKey(User, related_name="solicitante")
    servicio = models.ForeignKey(Servicio, related_name="tema")

    # Estos dos campos deben servir para mantener el estado de la conversación
    # si uno de los dos está a true para esa parte no será mostrada y para la
    # otra será mostrada cómo desactivado, si ambos a true se borrará de la BD.
    oferente_borrar = models.BooleanField(default=False)
    solicitante_borrar = models.BooleanField(default=False)

    class Meta:
        # Sólo puede haber un contacto de intercambio por 2 usuarios y 1
        # servicio
        unique_together = (("oferente", "solicitante", "servicio"), )
        verbose_name = "Contacto para intercambio"
        verbose_name_plural = "Contactos establecidos para intercambio"

    def __unicode__(self):
        return "Contacto, %s -> oferente: %s, solicitante %s" %\
                (self.servicio, self.oferente, self.solicitante)

    def resumenTema(self):
        return "%s..." % self.servicio.descripcion[:40]

    def descripcion_del_servicio(self):
        return self.servicio.descripcion


class ContactoAdministracion(models.Model):

    usuario_normal = models.ForeignKey(User, related_name="usuario_normal")
    administrador = models.ForeignKey(User, related_name="administrador")

    #Estos dos campos deben servir para mantener el estado de la conversación
    administrador_borrar = models.BooleanField(default=False)
    usuario_borrar = models.BooleanField(default=False)

    tema = models.CharField("Asunto", max_length=30)

    class Meta:
        unique_together = (("usuario_normal", "administrador"),)
        verbose_name = "Contacto con la administración"
        verbose_name_plural = "Contactos con la administración"

    def __unicode__(self):
        return "Contacto, administrador:%s usuario: %s" %\
               (self.administrador, self.usuario_normal)


class Mensaje(models.Model):

    contenido = models.TextField(max_length=400)
    pub_date = models.DateTimeField("Fecha de envío", auto_now=True)

    class Meta:
        abstract = True
        ordering = ['pub_date']


class MensajeI(Mensaje):

    contactoint = models.ForeignKey(ContactoIntercambio)

    # Indica el sentido del mensaje, desde el oferente hacia el
    # solicitante(true) o viceversa(false), no nos hacen falta los nombres
    # porque ya los tenemos en el contacto, así se lee mucha menos información
    # de la BD y también se almacena menos información inecesaria.

    o_a_s = models.BooleanField("de oferente a solicitante", )

    def __unicode__(self):
        if self.o_a_s:
            msj = "Mensaje %s de %s a %s" % (self.id,
                                             self.contactoint.oferente,
                                             self.contactoint.solicitante)
        else:
            msj = "Mensaje %s de %s a %s" % (self.id,
                                             self.contactoint.solicitante,
                                             self.contactoint.oferente)
        return msj

    class Meta:
        verbose_name = "Mensaje para intercambio"
        verbose_name_plural = "Mensajes para intercambios"


class MensajeA(Mensaje):

    contactoadm = models.ForeignKey(ContactoAdministracion)
    #Idem que para o_a_s
    a_a_u = models.BooleanField("de administrador a usuario", )

    def __unicode__(self):
        if self.a_a_u:
            msj = "Mensaje %s de %s a %s" % (self.id,
                                             self.contactoadm.administrador,
                                             self.contactoadm.usuario_normal)
        else:
            msj = "Mensaje %s de %s a %s" % (self.id,
                                             self.contactoadm.usuario_normal,
                                             self.contactoadm.administrador)
        return msj

    class Meta:

        verbose_name = "Mensaje con la administración"
        verbose_name_plural = "Mensajes con la administración"


TRANSFER_STATUS = (
    ('q', _('solicitada')), # q for reQuest
    ('a', _('aceptada')), # a for Accepted
    ('r', _('rechazada')), # r for Rejected
    ('d', _('realizada')), # d for Done
)

class Transfer(models.Model):
    rating = RatingField(range=5, allow_anonymous=False, can_change_vote=True)

    def int_rating(self):
        return int(self.rating.score / self.rating.votes)

    # Person receiving the credits (and giving the service)
    credits_payee = models.ForeignKey(Profile, related_name='transfers_received')

    # Person giving the credits (and receiving the service)
    credits_debtor = models.ForeignKey(Profile, related_name='transfers_given')

    service = models.ForeignKey(Servicio, related_name='transfers')

    # Small description for the received service
    description = models.TextField(_(u"Descripción"), max_length=300)

    request_date = models.DateTimeField(_("Fecha de solicitud de transferencia"), auto_now=True,
        auto_now_add=True)

    confirmation_date = models.DateTimeField(_(u"Fecha de confirmación de"
        " transferencia"),null=True)

    status = models.CharField(_(u"Estado"), max_length=1, choices=TRANSFER_STATUS)

    is_public = models.BooleanField(_(u"Transferencia pública"), default=False)

    # credits in minutes
    credits = models.PositiveIntegerField(_(u"Créditos"))

    #TODO: Add here a rating of the service, set by the payee of course

    class meta:
        ordering = ['-request_date']

    def creator(self):
        return self.service.creador == self.credits_debtor and\
            self.credits_payee or self.credits_debtor

    def status_readable(self):
        return TRANSFER_STATUS[self.status]

signals.post_save.connect(new_transfer_email, sender=Transfer)
