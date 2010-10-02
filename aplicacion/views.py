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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from models import UserForm, PerfilForm, PerfilUsuario, UpdatePerfUsuForm, ComentarioForm, Comentario, Transferencia, TxForm
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from serv.views import *

def registro(request):
	"""
	Devuelve un formulario vacío en caso de que se haya solicitado la página por primera vez
	o un formulario con los datos anteriores y sus errores
	o procesa los datos de un usuario proporcionados a través del formulario
	"""
	if request.method == 'POST': # Si el formulario ha sido enviado...
		form = UserForm(request.POST) # Un formulario conteniendo el postData
		form2 = PerfilForm(request.POST) #Crea un conjunto de datos que contendrá todos los datos extraídos de POST relacionados con el form.
		if form.is_valid(): # Pasa todas las validaciones
			if form2.is_valid():
				instanciaUsuario = form.save(commit=False) #Guardamos la primera parte de datos del usuario, instanciaUsuario es necesario porque aqui ya tenemos al nuevo usuario(parte de sus datos con su id) que nos hará falta para asociarlo al perfil
				instanciaUsuario.is_active = False #Comentar esta linea para evitar la validacion de los datos por administradores en el registro.
				instanciaUsuario.save()
				extraform2 = form2.save(commit=False) #Guardamos los datos en una instancia para que los podamos editar, pero aun no en la BD porque no hemos dicho a que usuario pertenece este perfil
				extraform2.user = instanciaUsuario
				extraform2.save()
				#pdb.set_trace()
				msjAdm = "Se ha registrado un nuevo usuario con nombre de usuario: %s . Revise sus datos y delo de alta."%instanciaUsuario.username
				#send_mail("Nuevo usuario registrado", msjAdm, 'ORIGEN',['DESTINATARIO'])
				return redirect(regExito) # Redirigimos tras POST
	else:
		form = UserForm() # Un formulario vacío
		form2 = PerfilForm()

	return render_to_response('registro.html', {
										'form': form,
										'formP': form2,
										'sectiontitle': 'Página de registro'
							})

def regExito(request):
	"""
	Página de redirección cuando se ha completado el registro con éxito
	"""
	return render_to_response('registroExito.html',{})
								
@login_required
def personal(request):
	"""
	Comprueba si se ha actualizado los datos del usuario y permite cambiarle su contraseña
	"""
	usu = request.user
	if float(usu.get_profile().saldo) < 0:
		color="red"
	else:
		if float(usu.get_profile().saldo) == 0:
			color="teal"
		else:
			color="blue"
	
	set_tx = Transferencia.objects.filter(Q(deudor=request.user)|Q(beneficiario=request.user))
	set_tx = set_tx.filter(realizada = True).order_by('-fechaTx') #Filtro todas las transferencias realizadas en las que he intervenido

	
	#No puedo usar el método predefinido "update_object" dado que tengo dos modelos, con dos formularios distintos ¿por qué? porque un formulario (desgraciadamente) no puede heredar de dos modelos simultaneamente.
	# El formulario debe manejar dos atributos con el mismo nombre 'id' tanto de perfil cómo de usuario.
	if request.method == 'POST':
		form = UpdatePerfUsuForm(request.POST)  #Todos los datos enviados
		if request.POST.__contains__('changeData'):#Cambio datos personales
			
			if form.is_valid(): #Actualizar datos
				msjAntiguo = "Datos antiguos del usuario:%s  : Nombre: %s, Apellidos: %s, Direccion: %s, Fecha nacimiento: %s, Email: %s"%(usu.username,usu.first_name,usu.last_name,usu.get_profile().direccion,usu.get_profile().fecha_de_nacimiento,usu.email)
				usu.first_name = request.POST.get('first_name','')
				usu.last_name = request.POST.get('last_name','')
				usu.email = request.POST.get('email','')
				usu.save() #NO-Guarda todos los nuevos datos de usuario ya que nuestro form hereda del model usuario, pero no los de PerfilUsuario
				data = {	'id': usu.get_profile().id,
					'user_id': usu.id,
					'direccion': request.POST.get('direccion',''),
					'fecha_de_nacimiento': request.POST.get('fecha_de_nacimiento',''),
					'descr': usu.get_profile().descr,
				}
				
				perf = PerfilForm(data)
				if perf.is_valid():
					instancia = perf.save(commit=False)
					instancia.user_id = request.user.id
					instancia.id = usu.get_profile().id
					instancia.save()

				msj = "Datos personales actualizados con éxito."
				
				#send_mail("Usuario cambio datos personales", msjAntiguo, 'ORIGEN',['DESTINATARIO'])
				# * Enviar email a la administración comunicando los datos nuevos(se pueden verificar en la BD) y antiguos, sino un usuario podría cambiar todos sus datos y noquedaría rastro
			else:
				msj = "Datos personales NO actualizados, corrija los datos erróneos."
			
		else: #Cambió la descripción
			descripcion = request.POST.get('descr','')
			if len(descripcion) < 150:
				perf = PerfilUsuario.objects.get(id = usu.get_profile().id)
				perf.descr = descripcion
				perf.save()
				msj = "Descripción de si mismo actualizada con éxito."
			else:
				msj = "Error, la descripción no debe contener más de 150 caracteres y la actual contiene %s."%len(descripcion)
		usu.message_set.create(message=msj)
			
	else: #si aun no he enviado datos nuevos (es la primera vez que accedo a la página)
			# Saco los datos del usuario para presentarlos
		data = { 	'first_name': usu.first_name,
					'last_name': usu.last_name,
					'email': usu.email,
					'fecha_de_nacimiento': usu.get_profile().fecha_de_nacimiento,
					'direccion': usu.get_profile().direccion,
					'descr': usu.get_profile().descr,
				}
		form = UpdatePerfUsuForm(data)
	
	return render_to_response('personal.html', {
										'form': form,
										'sectiontitle': 'Página personal',
										'nombre_usuario': usu.username,
										'color': color,
										'messages': usu.get_and_delete_messages()[:5],
										'usu': usu,
										'set_tx': set_tx,
							})
	
								
@login_required
def baja(request):
	pregunta = 'hidden'
	baja = 'submit'
	msj = ""
	motivo = ''
	disabled = ''
	if request.method == 'POST':
		if request.POST.__contains__('BajaSi'):
			usu=request.user
			usu.is_active = False
			usu.save()
			msjAdmin = "El usuario:%s se ha dado de baja."%usu.username
			#send_mail("Usuario de baja", msjAdmin, 'ORIGEN',['DESTINATARIO'])
			from django.contrib.auth import views as m
			#return m.login(request, 'login.html')
			return redirect(m.login)
		
		elif request.POST.__contains__('BajaNo'):
			pregunta = 'hidden'
			baja = 'submit'
		else:
			motivo = request.POST.get('motivo','')
			if len(motivo) < 2:
				msj = "Por favor introduzca el motivo de su baja"
			else:
				disabled = 'disabled'
				msj = "¿Está seguro que desea darse de baja?"
				pregunta = 'submit'
				baja = 'hidden'
		
	return render_to_response('baja.html', {
										'sectiontitle': 'Se está dando de baja...',
										'nombre_usuario': request.user.username,
										'messages': request.user.get_and_delete_messages(),
										'pregunta': pregunta,
										'baja': baja,
										'msj':msj,
										'motivo': motivo,
										'disabled': disabled,
								})
								
@login_required
def publico(request, id_usu=1):
	if id_usu=='1': #Si accedemos a la página sin argumentos, se muestra nuestro propio perfil.
		id_usu = request.user.id
	
	if request.method == 'POST': #Entramos por post al borrrar, si queremos comentar nos redirige a otra vista
		id_usu = request.POST.get('id_usu','')
		if request.POST.has_key('borrarC'):#Decidimos borrar nuestro comentario sobre otro
			try:
				usu_perfil = User.objects.get(id = id_usu)#usu_perfil representa el usuario que visualizamos
				media = float(usu_perfil.get_profile().puntGlob.replace(",",".")) #Viene de la forma commaseparetedintegerfield
				cont = Comentario.objects.filter(destinatario = id_usu).count() #El nr. de comentarios del usuario
				comment = Comentario.objects.get(id = request.POST['id_comment']) #El comentario a borrar
				if int(cont) == 1: #El nuestro era el único comentario
					usu_perfil.get_profile().puntGlob = 22 #Reseteamos a la puntuación por defecto que usamos como marcador de que nadie ha comentado
				else: #Sino contamos cuantos comentarios tiene el usario, multiplicamos la media por ese número, le restamos la puntuación del comentario a borrar y lo dividimos entre nr.comentarios-1
					quita_punt = float(comment.puntuacion.replace(",","."))#Normalizamos la punt. a borrar
					media = (media*cont-quita_punt)/(cont-1)#Pura matemática, asi no nos hace falta sacar todas las puntuaciones hasta ahora habidas.
					usu_perfil.get_profile().puntGlob = str(round(media,2)).replace(".",",")
				usu_perfil.get_profile().save()#Guardamos el perfil actualizado
				comment.delete()#Y borramos el comentario
			except:
				request.user.message_set.create(message="No se ha podido acceder al comentario indicado, intentelo de nuevo.")
	else:
		pagina = int(request.GET.get('pagina', '1'))#Capturamos a que página queremos ir
		#id del usuario visualizado se debe guardar para cuando se solicite comentar sobre el
	mostrar = User.objects.get(id=id_usu)
	titulo = "Perfil público del usuario:" 
	comentario_set = Comentario.objects.filter(destinatario = mostrar.id).order_by('-pub_date')
	#inicio paginación
	paginacion = Paginator(comentario_set, 7)
	try:
		comentario_set = paginacion.page(pagina) #Si intentamos ir a una página más allá de las q hay
	except:
		comentario_set = paginacion.page(paginacion.num_pages)#Nos dirigimos a la última.
	
	#fin paginación
	return render_to_response('publico.html', {
										'sectiontitle': titulo,
										'nombre_usuario': request.user.username,
										'usu_m':mostrar,
										'messages': request.user.get_and_delete_messages(),
										'id_usu': id_usu,
										'comentario_set': comentario_set,
										'usu_accede': request.user,
																		
								})
@login_required							
def comentar(request, id_usu=1):
	form = ComentarioForm()
	if request.method == 'POST':
		id_usu = request.POST.get('id_usu','')
		if int(id_usu) == int(request.user.id):#Un usuario no puede comentar sobre si mismo
			request.user.message_set.create(message="No puedes comentar sobre tí mismo!!")
			return publico(request) #redirect(publico)
			#return HttpResponseRedirect('/publico/')
		destinatario = User.objects.get(id=id_usu)
		if not request.POST.__contains__('deseoC'):#Cuando venimos de la página principal de perfil NO comprobamos el formulario, pues seguro q está vacío
			form = ComentarioForm(request.POST) 
			if form.is_valid():
					instance = form.save(commit=False)#Guardamos comentario y puntuación
					instance.destinatario_id = id_usu
					instance.autor_id = request.user.id
					#Hay que actualizar la puntuación global del destinatario
					media = float(destinatario.get_profile().puntGlob.replace(",",".")) #Viene de la forma commaseparetedintegerfield
					if media == 22:#Si es el primer comentario
						destinatario.get_profile().puntGlob = instance.puntuacion
					else:#Sino contamos cuantos comentarios tiene el usario, multiplicamos la media por ese número, le sumamos la nueva puntuación al comentario y lo dividimos entre nr.comentarios+1
						cont = Comentario.objects.filter(destinatario = id_usu).count()
						nueva_punt = float(instance.puntuacion.replace(",","."))
						media = (media*cont + nueva_punt)/(cont + 1)#> s = str(round(x,2))
						destinatario.get_profile().puntGlob = str(round(media,2)).replace(".",",")#En primer lugar redondeamos a 2 posiciones detrás del punto.
					destinatario.get_profile().save()#Guardamos el perfil actualizado
					instance.save() #Guardamos el nuevo comentario
					msj = "Has enviado un comentario sobre %s"%destinatario.username
					request.user.message_set.create(message=msj)
					#Tambien creamos un mensaje al usuario destinatario.
					msj2= "Has recibido un comentario de %s. Verificalo en tu seccion de 'Perfil Publico'."%request.user.username
					destinatario.message_set.create(message=msj2)
					return publico(request, id_usu=id_usu)
					#return HttpResponseRedirect('/publico/%s'%id_usu)
			
		
	else:
		destinatario = User.objects.get(id=id_usu)
	titulo = "Estas comentando sobre el usuario: %s"%destinatario.username
	
	return render_to_response('comentar.html', {
										'sectiontitle': titulo,
										'nombre_usuario': request.user.username,
										'usu_m':destinatario,
										'form': form,
										'messages': request.user.get_and_delete_messages(),
										'id_usu': id_usu,
																		
								})

@login_required					
def transferencia(request):
	"""
	Vista que gestiona la creación de una transferencia nueva.
	"""
	form = TxForm()
	texto_usuario = ""
	usuario_exacto = ""
	msj_error = ""
	msj_exito = ""
	ofrece = ""
	ofrece_chkd = ""
	solicita_chkd = ""
	# pdb.set_trace()
	if request.method == 'POST':
		form = TxForm(request.POST)
		usuario_exacto = request.POST['usuarioD']

		if request.POST.has_key('ofrecer'):
			ofrece = int(request.POST['ofrecer']) #Transforma de unicode a integer
			if ofrece:
				ofrece_chkd = "checked"
			else:
				solicita_chkd = "checked"
			
		if request.POST.has_key('buscarUsu'): #Hemos decidido buscar el nombre de usuario exacto porque no estamos seguros
			#un campo de texto siempre va a estar en el diccionario request.POST aunque con sea el string vacío ""
			set_usuarios = User.objects.filter(username__icontains = usuario_exacto)[:15] #Para no saturar la pág. si hay muchas coincidencias sólo mostraremos las quince primeras
			texto_usuario = "Se han encontrado diversos usuarios según la descripción: "
			for usu in set_usuarios:
				texto_usuario += str(usu.username) + ", "
			texto_usuario += "escriba el correcto en la caja de texto."	

			if len(set_usuarios) == 1:
				usuario_exacto = usu.username
				texto_usuario = "Sólo hay un resultado que coincidió con tu búsqueda.(El indicado en la caja de texto)"
			if len(set_usuarios) == 0:
				texto_usuario = "Lo sentimos, no hay ningún usuario que concuerde, pruebe otra vez. Intente hacer la palabra más corta."
							
		else:#Hemos decidido enviar la transferencia
			 #Comprobamos si se han insertado todos los datos
			if form.is_valid():
				if request.POST.has_key('ofrecer'):	#Podríamos separarlos para indicar cada error en específico
					try:
						usu = User.objects.get(username = usuario_exacto) #En caso de que no exista el usuario, no seguiremos pues saltará la excepción.
						if not usu == request.user: #No te hagas transferencias a ti mismo
							instanciaTx = form.save(commit=False)#Guardamos la descr. y cantidad en una instancia transferencia.
							#Marcamos a favor de quien y procedente de que cuenta se realizará la transferencia
							if ofrece: #Si el usuario que envía la Tx le ha ofrecido un servicio al que se la envía:
								limite = float(request.user.get_profile().saldo) + float(instanciaTx.cantidad.replace(",","."))
								if limite < 10.5:#Menor que 10,5 porque el máx. permitido es 10. y va de 0,5 en 0,5
									instanciaTx.creoBeneficiario = True #Yo creé la tx
									instanciaTx.beneficiario = request.user #Yo soy el beneficiario
									instanciaTx.deudor = usu
									instanciaTx.save()
									#Creamos un mensaje al otro usuario para que vea que tiene una transferencia pendiente
									msj2 = "El usuario: %s te ha enviado una solicitud de transferencia. Verificalo en tu seccion de mensajes y transferencias."%request.user.username
									usu.message_set.create(message = msj2)
									# XXX: Pablo added this
									msg_email = "Tienes una nueva solicitud de transferencia de %s que espera respuesta.\n\nAccede a la web del Banco del Tiempo del Ecolocal y consulta 'Conversaciones y transferencias'.\n\nhttp://www.ecolocal.es\n"%request.user.username
									send_mail("BdT Ecolocal: Nueva solicitud de transferencia espera respuesta", msg_email, 'ecolocal@gmail.com', [usu.email])
									return redirect(mensajesTransf)
									#return HttpResponseRedirect('/mensajes/')#Redireccionamos a la página donde el usuario podrá ver su Tx
								else:
									msj_error = "No puede tener más de +10créditos y en caso de que la transferencia fuera aceptada, excedería el límite."
							else: #En caso contrario
								#Si no tengo suficientes créditos en caso de que la tx sea aceptada
								limite = float(request.user.get_profile().saldo) - float(instanciaTx.cantidad.replace(",","."))
								if limite > -10.5:
									instanciaTx.creoBeneficiario = False
									instanciaTx.beneficiario = usu # El otro es el beneficiario
									instanciaTx.deudor = request.user # y yo soy el que paga
									instanciaTx.save()
									#Creamos un mensaje al otro usuario para que vea que tiene una transferencia pendiente
									msj2 = "El usuario: %s te ha enviado una solicitud de transferencia. Verificalo en tu seccion de mensajes y transferencias."%request.user.username
									usu.message_set.create(message = msj2)
									# XXX: Pablo added this
									msg_email = "Tienes una nueva solicitud de transferencia de %s que espera respuesta.\n\nAccede a la web del Banco del Tiempo del Ecolocal y consulta 'Conversaciones y transferencias'.\n\nhttp://www.ecolocal.es\n"%request.user.username
									send_mail("BdT Ecolocal: Nueva solicitud de transferencia espera respuesta", msg_email, 'ecolocal@gmail.com', [usu.email])
									#request.method = "GET"
									return redirect(mensajesTransf)
									#return HttpResponseRedirect('/mensajes/')#Redireccionamos a la página donde el usuario podrá ver su Tx
								else:
									msj_error = "No puede tener menos de -10créditos y si esta petición fuera aceptada se pasaría el límite."					
						else:
							msj_error = "No puede realizarse transferencias a ud. mismo, elija otro usuario."
					
					except User.DoesNotExist:#DoesNotExist: #Capturamos la userdoesnotexist excepción. NameError
						msj_error = "El usuario al que intentó realizar la transferencia no existe, indique el nombre exacto."

				else:
					msj_error = "Marque si ha realizado o ha recibido el servicio, por favor."
	return render_to_response('transferencia.html', {
										'sectiontitle': 'Está creando una petición de transferencia',
										'nombre_usuario': request.user.username,
										'form': form,
										'texto_usuario': texto_usuario,
										'usuario_exacto': usuario_exacto,
										'msj_error': msj_error,
										'msj_exito': msj_exito,
										'ofrece': ofrece,
										'ofrece_chkd': ofrece_chkd,
										'solicita_chkd': solicita_chkd,		
								})

								
def recuerdoClave(request):
	msj=""
	if request.method == "POST":
		msj = "Su usuario y cuenta de mail no han coincidido, por favor intentelo de nuevo."
		try:
			if request.POST.has_key('recuerdo'):
				usu = User.objects.get(username=request.POST['nom_usu'], email=request.POST['email'])
				pwd = User.objects.make_random_password(length=7, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
				usu.set_password(pwd)
				message = "%s,\n\nTu nueva clave es: %s\n\nPuedes cambiar esta clave desde tu pagina personal, en la barra de opciones que se encuentra abajo a la derecha."%(usu.username, pwd)
				#usu.email_user("BdT: El Ecolocal le dá una nueva contraseña", message, 'tim.gaggstatter@gmx.net' )
				send_mail("BdT: Nueva contraseña", message, 'ecolocal@gmail.com', [usu.email])
				usu.save()
				msj = "Se le ha enviado una nueva clave, comprueba tu correo tras unos minutos."
		except:
			msj="Su usuario y email no concuerdan, inténtelo de nuevo."
	return render_to_response('recuerdoClave.html', {
										'sectiontitle': 'Está pidiendo que le envien una nueva clave',
										'msj': msj,																		
								})

@login_required
def cambioPwd(request):
	#pdb.set_trace()
	if request.method == "POST":
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			form.save()
			return redirect(pwdCambiado)
		else:
			pass
	else:
		form = PasswordChangeForm(request.user)
	return render_to_response('cambiopwd.html', {
								'form': form,
								'nombre_usuario' : request.user.username,
								'sectiontitle': "¿Desea cambiar su contraseña?",
								})
def pwdCambiado(request):
	return render_to_response('cambiopwdhecho.html', {'nombre_usuario' : request.user.username, 'sectiontitle': "Contraseña cambiada",})

def dummy_mail(request):
	send_mail("Nuevo usuario registrado", "Contenido del mensaje", 'bdt@ecolocal.es',['tim.gaggstatter@gmx.net'])
	return render_to_response('registroExito.html',{})
