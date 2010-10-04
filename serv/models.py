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
from django import forms
import pdb
# Create your models here.
# ============= MODELOS ======================================

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
	creador = models.ForeignKey(User, related_name="creador")
	oferta = models.BooleanField()#Si es una oferta=true, si es demanda = false
	pub_date = models.DateTimeField("Fecha de publicación", auto_now=True, auto_now_add=True)
	activo = models.BooleanField(default=True)
	descripcion = models.TextField("Descripción", max_length=400)
	
	categoria = models.ForeignKey(Categoria)
	zona = models.ForeignKey(Zona)
	
	def __unicode__(self):
		if self.oferta:
			msj = "ofertado"
		else:
			msj = "solicitado"
		return "Servicio %s %s por: %s"%(self.id, msj, self.creador)
	def cortaServicio(self):#Recorta el servicio a 50 caracteres para su presentación en lista de administradores.
		return "%s..."%self.descripcion[:50]
		
class ContactoIntercambio(models.Model):
	oferente = models.ForeignKey(User, related_name="oferente")
	solicitante = models.ForeignKey(User, related_name="solicitante")
	servicio = models.ForeignKey(Servicio, related_name="tema")
	oferente_borrar = models.BooleanField(default=False) #Estos dos campos deben servir para mantener el estado de la conversación,
	solicitante_borrar = models.BooleanField(default=False) # si uno de los dos está a true para esa parte no será mostrada y para la otra será mostrada cómo desactivado, si ambos a treu se borrará de la BD.
	class Meta:
		unique_together = (("oferente", "solicitante", "servicio"),) #Sólo puede haber un contacto de intercambio por 2 usuarios y 1 servicio
		verbose_name = "Contacto para intercambio"
		verbose_name_plural = "Contactos establecidos para intercambio"
	def __unicode__(self):
		return "Contacto, %s -> oferente: %s, solicitante %s"%(self.servicio, self.oferente, self.solicitante)
	def resumenTema(self):#Descripcion corta para la interfaz de admin.
		return "%s..."%self.servicio.descripcion[:40]
	def descripcion_del_servicio(self):
		return self.servicio.descripcion
		
class ContactoAdministracion(models.Model):
	usuario_normal = models.ForeignKey(User, related_name="usuario_normal")
	administrador = models.ForeignKey(User, related_name="administrador")
	administrador_borrar = models.BooleanField(default=False) #Estos dos campos deben servir para mantener el estado de la conversación,
	usuario_borrar = models.BooleanField(default=False)
	tema = models.CharField("Asunto", max_length=30)
	class Meta:
		unique_together = (("usuario_normal", "administrador"),)
		verbose_name = "Contacto con la administración"
		verbose_name_plural = "Contactos con la administración"
	def __unicode__(self):
		return "Contacto, administrador:%s usuario: %s"%(self.administrador, self.usuario_normal)
		
class Mensaje(models.Model): #Creamos una clase abstracta ya que los mensajes entre dos usuarios por un servicio y entre un usuario y un administrador tendrán mucha información en común
	contenido = models.TextField(max_length = 400)
	pub_date = models.DateTimeField("Fecha de envío", auto_now=True)
	class Meta:
		abstract = True
		ordering = ['pub_date']
		
		
class MensajeI(Mensaje):
	contactoint = models.ForeignKey(ContactoIntercambio)
	#Indica el sentido del mensaje, desde el oferente hacia el solicitante(true) o viceversa(false), no nos hacen falta los nombres 
	#porque ya los tenemos en el contacto, así se lee mucha menos información de la BD y también se almacena menos información inecesaria.
	o_a_s = models.BooleanField("de oferente a solicitante",)
	def __unicode__(self):
		if self.o_a_s:
			msj =  "Mensaje %s de %s a %s"%(self.id, self.contactoint.oferente, self.contactoint.solicitante)
		else:
			msj = "Mensaje %s de %s a %s"%(self.id, self.contactoint.solicitante, self.contactoint.oferente)
		return msj
	class Meta:
		verbose_name = "Mensaje para intercambio"
		verbose_name_plural = "Mensajes para intercambios"
			
class MensajeA(Mensaje):
	contactoadm = models.ForeignKey(ContactoAdministracion)
	a_a_u = models.BooleanField("de administrador a usuario",) #Idem que para o_a_s
	def __unicode__(self):
		if self.a_a_u:
			msj =  "Mensaje %s de %s a %s"%(self.id, self.contactoadm.administrador, self.contactoadm.usuario_normal)
		else:
			msj = "Mensaje %s de %s a %s"%(self.id, self.contactoadm.usuario_normal, self.contactoadm.administrador)
		return msj
	class Meta:
		verbose_name = "Mensaje con la administración"
		verbose_name_plural = "Mensajes con la administración"
	
	
# ==================== FORMULARIOS ======================================
		
class ServicioForm(forms.ModelForm):
	OFERTA_CHOICES = (
		('0','DEMANDA'),
		('1','OFERTA'),
	
	)
	oferta = forms.CharField(label="Crear una", help_text=", debe elegir si es una oferta(ofrece algo) o una demanda(solicita algo)", widget=forms.Select(choices=OFERTA_CHOICES))
	class Meta:
		model = Servicio
		exclude = ('creador', 'pub_date', 'activo')
	
	def clean_oferta(self):
		oferta = self.cleaned_data.get("oferta", "")	
		if int(oferta): #Al ser el campo de tipo char nos lo devuelve cómo unicode (string) u'0' lo convertimos a entero y sacamos si es verdadero o falso para almacenarlo en la BD
			oferta = 1
		else:
			oferta = 0
		return oferta
	def clean_descripcion(self):
		descr = self.cleaned_data.get("descripcion","")
		if len(descr)>400:
			raise forms.ValidationError("La descripcion no debe pasar de 400caracteres, la actual tiene %s"%len(descr))
		return descr
		
class ContactoIForm(forms.ModelForm):
	class Meta:
		model = ContactoIntercambio
		
class MensajeIForm(forms.ModelForm):
	class Meta:
		model = MensajeI
		fields = ['contenido',]
	def clean_contenido(self):
		conte = self.cleaned_data.get("contenido","")
		if 1 >len(conte) or  len(conte)> 400:
			raise forms.ValidationError("El comentario debe tener entre 1 y 400 caracteres y el actual tiene %s."%len(conte))
		return conte
		
		