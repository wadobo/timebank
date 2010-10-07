# -*- coding: utf-8 -*- 
# Copyright (C) 2009 Tim Gaggstatter <Tim.Gaggstatter AT gmx DOT net>
# Copyright (C) 2010 Eduardo Robles Elvira <edulix AT gmail DOT com>
# Copyright (C) 2010 Daniel Garcia Moreno <dani AT danigm DOT com>
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
from django import forms
from django.contrib.localflavor.generic.forms import DateField
from django.utils.encoding import smart_unicode

DEFAULT_DATE_INPUT_FORMATS = '%d/%m/%y'

class PerfilUsuario(models.Model):
    user = models.ForeignKey(User, unique=True, related_name="Perfil de usuario")

    fecha_de_nacimiento = models.DateField()

    direccion = models.CharField("Dirección", max_length=100,
        help_text="Con que indique la calle y el número es suficiente " \
        "(presuponemos que reside en Sevilla)")

    saldo = models.DecimalField(max_length=4, max_digits=3, decimal_places=1,
        default=0, help_text="Para separar la parte decimal se usan puntos, " \
        "no comas.")

    descr = models.TextField("Descripción de si mismo", max_length=150,
        blank=True)

    puntGlob = models.CommaSeparatedIntegerField("Puntuación global",
        default=22, max_length=4)
    
    class meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"
    
    def __unicode__(self):
        return "Id: %s usuario: %s"%(self.id, self.user.username)
        
class Comentario(models.Model):
    autor = models.ForeignKey(User, related_name="autor")

    destinatario = models.ForeignKey(User, related_name="destinatario")

    contenido = models.TextField(max_length=200)

    puntuacion = models.CommaSeparatedIntegerField("Puntuación", max_length=4)

    pub_date = models.DateTimeField("Fecha de publicación", auto_now=True,
        auto_now_add=True)
    
    class meta:
        ordering = ['-pub_date']
    
    def __unicode__(self):
        return "Comentario de: %s a: %s en fecha: %s" % (self.autor,
            self.destinatario, self.pub_date)

    def contenidoCorto(self):
        return "%s..." % self.contenido[:30]

class Transferencia(models.Model):
    # The person who receives the credits for the service being given
    beneficiario = models.ForeignKey(User, related_name="beneficiario")
    
    # The person receiving the service, who pays in credits
    deudor = models.ForeignKey(User, related_name="deudor")

    creoBeneficiario = models.BooleanField()

    descrServ = models.TextField("El servicio de", max_length=40,
        help_text="indique una breve descripción del servicio en este apartado")

    fechaTx = models.DateTimeField("Fecha de solicitud de transferencia",
        auto_now=True)

    realizada = models.BooleanField("Si se ha realizado", default=False)

    rechazada = models.BooleanField("Si se ha rechazado", default=False)

    cantidad = models.CommaSeparatedIntegerField("CANTIDAD DE", max_length=3,   
        help_text="CRÉDITOS DE TIEMPO. Sólo se admiten cómo valores decimales" \
        " el 0 y el 5. Ejemplo: 1,5 o 2,0 o 1")

    class meta:
        ordering = ['-fechaTx']

    def __unicode__(self):
        return "Transferencia a favor de: %s procedente de: %s en fecha: %s" %\
            (self.beneficiario, self.deudor, self.fechaTx)
