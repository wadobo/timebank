# -*- coding: utf-8 -*- 
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
from django.contrib.localflavor.generic.forms import DateField
from django.utils.encoding import smart_unicode
# from django.forms.widgets import DateTimeInput

DEFAULT_DATE_INPUT_FORMATS = '%d/%m/%y'

# ============= MODELOS ======================================
class PerfilUsuario(models.Model):
	user = models.ForeignKey(User, unique=True, related_name="Perfil de usuario")

	fecha_de_nacimiento = models.DateField() #Será redefinido en el formulario que rellenará este model para permitir el formato de fecha tradicional
	direccion = models.CharField("Dirección", max_length=100, help_text="Con que indique la calle y el número es suficiente (presuponemos que reside en Sevilla)")
	saldo = models.DecimalField(max_length=4, max_digits=3, decimal_places=1, default=0, help_text="Para separar la parte decimal se usan puntos, no comas.") # son 4 para tener saldos entre -99,5 y 99,5 nunca más de un decimal ya que la unidad de intercambio mínima es la media hora (0,5)
	descr = models.TextField("Descripción de si mismo", max_length=150, blank=True) #Este campo no es obligatorio.
	puntGlob = models.CommaSeparatedIntegerField("Puntuación global", default=22, max_length=4) #son 4 para permitir puntuaciones entre 0 y 9,99, el default se reseteará con la primera puntuación
	
	class meta:
		verbose_name = "Perfil de usuario"
		verbose_name_plural = "Perfiles de usuario"
	
	def __unicode__(self):
		return "Id: %s usuario: %s"%(self.id, self.user.username)
		# A la hora de visualizar el objeto perfil se verá el nombre del usuario al que se refiere éste perfil.
		
class Comentario(models.Model):
	autor = models.ForeignKey(User, related_name="autor")
	destinatario = models.ForeignKey(User, related_name="destinatario")
	contenido = models.TextField(max_length=200) #Obligatorio siempre por defecto, no hay que especificarlo
	puntuacion = models.CommaSeparatedIntegerField("Puntuación", max_length=4)
	pub_date = models.DateTimeField("Fecha de publicación", auto_now=True, auto_now_add=True) #Campo será puesto en la fecha y hora actuales cuando se cree y siempre que se guarde.
	
	class meta:
		ordering = ['-pub_date'] #Siempre el comentario más reciente el primero
	
	def __unicode__(self):
		return "Comentario de: %s a: %s en fecha: %s"%(self.autor, self.destinatario, self.pub_date)
	#El verbose_name_plural(nombre visualizado para varios objetos) por defecto es nombre de la clase + 's'	, en este caso es correcto.
	def contenidoCorto(self):
		return "%s..."%self.contenido[:30]

class Transferencia(models.Model):
	beneficiario = models.ForeignKey(User, related_name="beneficiario")#Será el oferente del servicio, quien presta el servicio, le 'pagan'
	deudor = models.ForeignKey(User, related_name="deudor")#Será el solicitante del servicio, el que recibe el servicio, debe 'pagar'
	creoBeneficiario = models.BooleanField()#También nos hará falta almacenar la información de quien creó la tx, para indicarle al otro que debe aceptarla. El que creó la Tx no tiene que aceptarla otra vez!
	descrServ = models.TextField("EL SERVICIO DE",max_length=40,help_text="indique una breve descripción del servicio en este apartado")
	fechaTx = models.DateTimeField("Fecha de solicitud de transferencia", auto_now=True)
	realizada = models.BooleanField("Si se ha realizado", default=False)
	rechazada = models.BooleanField("Si se ha rechazado", default=False)
	cantidad = models.CommaSeparatedIntegerField("CANTIDAD DE", max_length=3, help_text="CRÉDITOS DE TIEMPO. Sólo se admiten cómo valores decimales el 0 y el 5. Ejemplo: 1,5 o 2,0 o 1")
	
	class meta:
		ordering = ['-fechaTx'] #La tx más reciente primero
		
	def __unicode__(self):
		return "Transferencia a favor de: %s procedente de: %s en fecha: %s"%(self.beneficiario, self.deudor, self.fechaTx)



# ==================== FORMULARIOS ===========================================
# Las dos clases siguientes son para los formularios correspondientes a la creación del usuario y sus datos asociados
class UserForm(forms.ModelForm): #Aquí no se describe la clase o modelo de usuario (sólo el formulario correspondiente) ya que usamos el que nos aporta django.
	pwd1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput) #Añadimos estos dos campos para hacer verificaciones sobre la contraseña
	pwd2 = forms.CharField(label="Confirmación de contraseña", widget=forms.PasswordInput, help_text="Repita la contraseña anterior, por favor.")
	email = forms.EmailField(label="Dirección de correo electrónico") #sobreescribimos los atributos de este campo, porque por defecto django nos proporciona un campo que no es obligatorio y tampoco es único, y queremos que se cumplan ambos(la obligatoriedad ya se tiene con solo redefinirlo, por defecto blank=false).
	username = forms.RegexField(label="Nombre de usuario", max_length=30, regex=r'^\w+$',
								help_text = "30 caracteres o menos, sólo alfanuméricos(letras,dígitos y guiones bajos)",
								error_message = "Sólo caracteres alfanuméricos.")
	first_name = forms.CharField(label="Nombre propio", max_length=30)
	last_name = forms.CharField(label="Apellidos", max_length=30) #ambos sobreescritos por no ser obligatorios en el modelo que nos suministra django
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email') #No queremos que el usuario pueda indicar su fecha de alta o asignarse permisos, etc, sólo elegimos los campos que nos hacen falta
	def clean_email(self): #Todo esto porque no queremos modificar las clases internas de django de usuario en donde bastaría poner en el modelo de usuario en el campo de email unique=true
		emailIntento = self.cleaned_data.get("email", "")
		u = User.objects.filter(email=emailIntento)
		if bool(u) == True: #Ya hay un usuario con este mail, bool(u) devuelve falso si u es una lista vacía (empty queryset),y justo cuando esto pasa es cuando queremos proceder y no entrar en la guarda del if
			raise forms.ValidationError("Por favor indique otro email, este ya está siendo usado por un usuario en el sistema")
		return emailIntento
	
	def clean_pwd2(self): #Comprobamos si las 2 contraseñas concuerdan
		pwd1 = self.cleaned_data.get("pwd1", "")
		if len(pwd1) < 5: #Clave al menos 5 caracteres
			raise forms.ValidationError("Su contraseña debe tener al menos 5 caracteres")
		pwd2 = self.cleaned_data["pwd2"]
		if pwd1 != pwd2:
			raise forms.ValidationError("Las dos contraseñas no coinciden.")
		return pwd2

	def save(self, commit=True): #Redefinimos el método save para que se adjunte el pwd codificado en la BD
		user = super(UserForm, self).save(commit=False) #Llamamos al método padre, sin commit(es decir aun no lo envíamos, sólo guardamos los datos a ser salvados en un objeto temporalmente)
		user.set_password(self.cleaned_data["pwd1"])
		if commit:
			user.save()
		return user
	
		
class PerfilForm(forms.ModelForm):
	# from django.contrib.localflavor.generic.forms import DateField #Para poder especificar en la fecha en el formato habiutal en españa, aunque en la BD si se guardará en el formato americano 'AAA-MM-DD', sólo hay que tener cuidado a la hora de mostrarlo al usuario
	fecha_de_nacimiento = DateField(help_text="Por favor use el siguiente formato: <em>DD/MM/AAAA</em>.")
	class Meta:
		model = PerfilUsuario
		verbose_name = "Perfil de usuario"
		exclude = ('user', 'saldo', 'puntGlob') #Excluimos el campo usuario (el usuario que se registra no debe poder modificar este campo), ya que debemos asignar el perfil al mismo usuario y no a uno cualquiera, lo hacemos una vez creada la primera parte de los datos de usuario y luego vinculandolo


class UpdatePerfUsuForm(forms.ModelForm):
	"""
	Esta clase debe representar un formulario para actualizar todos los datos del usuario,
	tanto los que provienen del modelo predefinido User cómo los que provienen de su perfil 
	PerfilUsuario, además se aporta un apartado (link) que servirá para, introduciendo la contraseña
	actual, poder cambiar a una nueva.
	"""
	# Datos de usuario
	email = forms.EmailField(label="Dirección de correo electrónico")
	first_name = forms.CharField(label="Nombre propio", max_length=30)
	last_name = forms.CharField(label="Apellidos", max_length=30)

	
	# Datos de perfil
	descr = forms.CharField(label="Descripción de si mismo", widget=forms.Textarea, required=False)
	fecha_de_nacimiento = DateField(help_text="Por favor use el siguiente formato: DD/MM/AAAA.")
	direccion = forms.CharField(label="Dirección", help_text="Con que indique la calle y el número es suficiente (presuponemos que reside en Sevilla)")

	#Métodos usuario
	class Meta:
		model = User
		verbose_name = "Perfil y usuario juntos"
		fields = ('first_name', 'last_name', 'email', )
		
	
class ComentarioForm(forms.ModelForm):
	class Meta:
		model = Comentario
		fields = ('contenido', 'puntuacion',) 
		
	def clean_puntuacion(self):
		punt = self.cleaned_data.get("puntuacion","")
		list = punt.split(',')
		try:
			entera = int(list[0])
			if (len(list) <> 2): #El usuario no ha puesto la coma, sólo 1 digito
				if -1 < entera < 11:#Admitimos el 0 y el 10
					return punt
				else:
					raise forms.ValidationError("Introduzca un valor entre 0 y 10")
			if (not -1 < entera < 10):#No se puede escribir 10,3 pero si 0,4
				raise forms.ValidationError("Introduzca un valor entre 0 y 10")
		except:
			raise forms.ValidationError("Introduzca un valor entre 0,00 y 10,0")
		return punt
		
	def clean_contenido(self):
		conte = self.cleaned_data.get("contenido","")
		if len(conte) > 200:
			raise forms.ValidationError("El comentario debe tener menos de 200 caracteres y el actual tiene %s."%len(conte))
		return conte
		

class TxForm(forms.ModelForm):
	class Meta:
		model = Transferencia
		fields = ('descrServ', 'cantidad',)
		
	def clean_descrServ(self):
		descr = self.cleaned_data.get("descrServ","")
		if not 0 < len(descr) < 40 :
			raise forms.ValidationError("Introduzca una breve descripción del servicio, entre 0 y 40 caracteres la actual tiene %s"%len(descr))
		return descr
	
	def clean_cantidad(self):
		cant = self.cleaned_data.get("cantidad","")
		list = cant.split(',')
		try:
			entera = int(list[0])
			if (len(list) <> 2): #El usuario no ha puesto la coma, sólo 1 digito
				if 0 < entera < 10:
					return cant
				else:
					raise forms.ValidationError("Introduzca un valor entre 0,5 y 9,5")
			decimal = int(list[1])
			if (not -1 < entera < 10) or (decimal <> 5 and decimal <> 0):
				raise forms.ValidationError("Introduzca un valor entre 0,5 y 9,5")
		except:
			raise forms.ValidationError("Introduzca un valor entre 0,5 y 9,5")
		return cant
			
