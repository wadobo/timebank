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
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.query import QuerySet, EmptyQuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.views.generic.create_update import update_object

from serv.models import (Servicio, Zona, Categoria,
                         ContactoIntercambio, MensajeI,
                         ContactoAdministracion, MensajeA)
from serv.forms import ServicioForm, ContactoIForm, MensajeIForm

from aplicacion.models import Transferencia
from aplicacion.views import *


@login_required
def misservicios(request):
    msj = ""
    valCreaServ = "Crear nuevo servicio"
    id_elemento = ""
    if request.method == 'POST' and request.POST.has_key('creaServ'):
        # Hemos decidido crear un nuevo servicio
        form = ServicioForm(request.POST)
        if form.is_valid():
            # Se guardan los datos en una instancia del tipo Servicio aunque
            # aun no se mandan a la BD porque falta completar quien es el
            # creador.
            instserv = form.save(commit=False)
            instserv.creador = request.user
            
            # Si estamos modificando un servicio (no queremos crear uno
            # nuevo)
            if request.POST.has_key('modified'):
                instserv.id = request.POST['id_modifica']

            # Guardamos el nuevo servicio creado
            instserv.save()
            msj = "has creado un nuevo servicio con éxito. Si lo deseas puedes verificarlo usando el buscador en la sección de oferta y demanda."

            # Devolvemos un formulario vacío por si se quiere crear otro
            # servicio
            form = ServicioForm()
    # Queremos modificar cualquiera de los servicios presentes
    elif request.method == 'POST':
        id_elemento = request.POST['id_elemento']
        set_elementos = funcAccion(request, id_elemento)
        if request.POST.has_key('Modificar'):
            return set_elementos
        if set_elementos.has_key('msj'):
            msj = set_elementos['msj']
        if set_elementos.has_key('form'):
            form = set_elementos['form']
    else:
        form = ServicioForm()

    # Llama a la función servSets
    set_completo = servSets(request.user)

    return render_to_response('servicios.html', {
        'sectiontitle': 'Mis servicios',
        'nombre_usuario': request.user.username,
        'form': form,
        'msj': msj,
        'ofreces': set_completo['ofrece_set'],
        'solicitas': set_completo['solicita_set'],
        'inactivos': set_completo['inactivo_set'],
        'valCreaServ': valCreaServ,
        # En lugar de pasar la variable otra vez al formulario para luego volver
        # a leerla se podría usar la variable session
        'id_modifica': id_elemento
    })


def servSets (usu):
    """
    Una función que nos devuelve un diccionario con los diferentes
    sets de servicios existentes de un usuario determinado.
    """

    set_completo = dict()
    set_completo['ofrece_set'] = Servicio.objects.filter(creador=usu, oferta=True, activo=True).order_by('-pub_date')
    set_completo['solicita_set'] = Servicio.objects.filter(creador=usu, oferta=False, activo=True).order_by('-pub_date')
    set_completo['inactivo_set'] = Servicio.objects.filter(creador=usu, activo=False).order_by('-pub_date')
    return set_completo


def funcAccion(request, id_elemento):
    """
    Según la acción(que nos indica el request)actua sobre el elemento cuyo id nos pasan como parámetro
    """

    form = ServicioForm()
    if request.POST.has_key('Eliminar'):
        Servicio.objects.get(pk = id_elemento).delete()
        msj = "has eliminado un servicio."
    elif request.POST.has_key('Modificar'):
        msj = "has decidido modificar un servicio."
        valCreaServ = "Guardar cambios"
        return update_object(request, 
            form_class=ServicioForm,
            object_id=id_elemento,
            # no se usa
            post_save_redirect="/servicios/",
            # Debería devolver el id de la zona y categoria actuales para
            # tenerlos preseleccionados en el menú desplegable
            template_name="modificarServ.html", 
            extra_context = {
                'lista_zonas': Zona.objects.all(),
                'lista_categorias': Categoria.objects.all(),
                'sectiontitle': 'Mis servicios - Editando',
            }
        )
    elif request.POST.has_key('Desactivar'):
        msj = "has decidido desactivar un servicio, este no será accesible por los demás usuarios hasta que vuelvas a activarlo."
        obj = Servicio.objects.get(pk = id_elemento)
        obj.activo = 0
        obj.save()
    else:
        # Activar un servicio desactivaod
        msj = "has decidido activar un servicio."
        obj = Servicio.objects.get(pk = id_elemento)
        obj.activo = 1
        obj.save()
        
    set_elementos = dict()
    set_elementos['msj'] = msj
    set_elementos['form'] = form
    return set_elementos


# END misservicios related

def buscador(request):
    set_solicitado = ""
    c = 0
    z = 0
    pagina = 1
    palabras = ""
    serv_chkd = "checked"
    usu_chkd = ""
    ambos = "checked"
    ofrecido = ""
    solicitado = ""
    msjs = []

    if request.method == 'POST' and request.POST.has_key('palabras'):
        # Si el campo de palabras no está vacío
        if not request.POST['palabras'] == "":
            request.session['palabras'] = request.POST['palabras']
            # Si queremos realizar una búsqueda por servicios
            if request.POST['group1'] == "Servicio":
                    request.session['serv_chkd'] = "checked"
                    request.session['usu_chkd'] = ""
                    # Separamos cada una de las palabras, como separador
                    # suponemos el espacio en blanco.
                    lista_palab = request.POST['palabras'].split()
                    todos = Servicio.objects.filter(activo = True)
                    # Esta es la alternativa que la descripción tenga que
                    # contener todas las palabras que ha introducido el usuario
                    for w in lista_palab:
                        # En cada iteración vamos refinando más el cjto. de
                        # elto. seleccionados
                        todos = todos.filter(descripcion__icontains=w)
                    set_solicitado = todos
                    if not set_solicitado:
                        # Si no hay ninguna resultado
                        msjs.append("No hay ningún servicio que coincida con tus criterios.")
                        # request.user.message_set.create(message=\"No hay "\
                        # "ningun servicio que coincida con tus criterios.")
                    #Y esta es la alternativa para que la descripción solamente
                    # tenga que contener alguna de las palabras insertadas por
                    # el usuario.
                    # querystring = Q()
                    # for w in lista_palab:
                        # Creamos la cadena de la consula con objetos Q(que se
                        # usan para consultas complejas)
                        # Si se insertan varias palabras, se devuelven todas las
                        # que contengan alguna de estas palabras
                        # querystring |= Q(descripcion__icontains=w)
                    # set_solicitado = Servicio.objects.filter(querystring)
            else:
                # Buscar por nombre de usuario
                request.session['serv_chkd'] = ""
                request.session['usu_chkd'] = "checked"
                querystring = Q()
                lista_palab = request.POST['palabras'].split()
                if lista_palab:
                    # Si la lista está vacía no podemos acceder ni al primer
                    # indice
                    # Puede devolver un cjto. de usuarios. Sólo se tiene en
                    # cuenta la primera palabra insertada en la caja de texto,
                    # los nombres de usuario nunca contiene espacios.
                    usu = User.objects.filter(username__icontains = lista_palab[0]) 
                    for usuario in usu: #Obtenemos una consulta por cada usuario
                        querystring |= Q(creador=usuario.id)
                    if querystring:
                        # Aplicamos las consultas y obtenemos todos los
                        # servicios pertenecientes a los usuarios, cuyos nombres
                        # de usuario incluyan la cadena insertada por el usuario
                        set_solicitado = Servicio.objects.filter(querystring, activo=True) 
                    else:
                        # Si no ha habido ningun usuario que coincidiera con
                        # nuestra palabra clave

                        # Debemos devolver un queryset vacio del tipo servicios
                        # para que las sucesivas filtraciones no den errores
                        set_solicitado = Servicio.objects.filter(creador = 700)
                        msjs.append("No hay ningún servicio que coincida con tus criterios.")
                        # request.user.message_set.create(message="No hay " \
                        # "ningun servicio que coincida con tus criterios.")
        # En este punto set_solicitado ya contendrá sólo los servicios que
        # pertenecen a un usuario (o a un cjto. de ellos) dtdo.
        # o un cjto. de servicios que en su descripción contiene las palabras
        # clave indicadas.
        # En caso de que hayamos dejado la caja de palabras clave en blanco, nos
        # devuelven todos los servicios ordenados, por los demás criterios
        # exceptuando usuario y servicio, pues es lo mismo devolver todos los
        # servicios que devolver los servicios de todos los usuarios
        else:
            # No hay palabras clave
            request.session['palabras'] = ""
            # En todos casos sólo queremos ver los servicios activos
            set_solicitado = Servicio.objects.filter(activo = True)
            if request.POST['group1'] == "Servicio":
                request.session['serv_chkd'] = "checked"
                request.session['usu_chkd'] = ""
            else:
                request.session['serv_chkd'] = ""
                request.session['usu_chkd'] = "checked"
            # Siguiente paso de filtración sólo si se ha elegido la opción
            # solicitado u ofrecido, si es ambos no realizamos nada 
        request.session['ambos'] = ""
        request.session['ofrecido'] = ""
        # Tb podríamos marcarlo con un número p.ej. 0,1,2 y compararlo en el template
        request.session['solicitado'] = ""
    
        if request.POST['group2'] == "Ambos":
            request.session['ambos'] = "checked"
        elif request.POST['group2'] == "Ofrecido":
            request.session['ofrecido'] = "checked"
            set_solicitado = set_solicitado.filter(oferta=1)
        else:
            #Servicios solicitados
            request.session['solicitado'] = "checked"
            set_solicitado = set_solicitado.filter(oferta=0)
    
        # Otros 2 pasos de filtración: por zona y por categoría
        c = int(request.POST['categoria'])
        if c:
            # En caso de que sea cero no se entra
            set_solicitado = set_solicitado.filter(categoria=c)
        request.session['c'] = c
        z = int(request.POST['zona'])
        if z:
            set_solicitado = set_solicitado.filter(zona=z)
        request.session['z'] = z


        # Finalmente ordenamos los servicios filtrados por fecha, la más 
        # reciente primero.
        set_solicitado = set_solicitado.order_by('-pub_date')
        # Guardamos en session la consulta, para cuando accedamos a posteriores
        # páginas no tengamos que volver a filtrar
        # Si no hay set_solicitado nuevo, no lo guarda (machaca).
        request.session['consulta'] = set_solicitado
    else:
        # Si hemos entrado por Get y no por Post y además en caso de venir desde
        # el metodo contactar
        if request.session.has_key('consulta'):
            # Al entrar por GET al consultar las páginas consecutivas a la
            # primera, no se machaca este queryset hasta que se haga una nueva
            # consulta.
            set_solicitado = request.session['consulta']
            
    #En todos casos
    if request.session.has_key('palabras'):
        palabras = request.session['palabras'] 
    if request.session.has_key('serv_chkd'):
        serv_chkd = request.session['serv_chkd']
    if request.session.has_key('usu_chkd'):
        usu_chkd = request.session['usu_chkd']
    if request.session.has_key('ambos'):
        ambos = request.session['ambos']
    if request.session.has_key('ofrecido'):
        ofrecido = request.session['ofrecido']
    if request.session.has_key('solicitado'):
        solicitado = request.session['solicitado']
    if request.session.has_key('c'):    
        c = request.session['c']
    if request.session.has_key('z'):
        z = request.session['z']

    # Añadiendo paginación, hay que guardar la consulta en session, cuando
    # accedemos a las otras páginas, accedemos por GET!
    paginacion = Paginator(set_solicitado, 7)
    try:
        if not request.method == "POST":
            # Si hemos hecho una consulta nueva, empezamos en la página primera.
            pagina = int(request.GET.get('pagina', '1'))
    except:
        pagina = 1
    try:
        servicios_buscados = paginacion.page(pagina)
    except:
        servicios_buscados = paginacion.page(paginacion.num_pages)

    if request.user.is_authenticated():
        # Para los usuarios registrados se mostrarán todos los detalles
        html_name = 'buscador.html'
        nom_usu = request.user.username
        cadena = str(request.user.get_and_delete_messages())
        # Quitamos que sea un elto. de lista unicode para imprimir
        cadena = cadena[3:(len(cadena)-2)]
        msjs.append(cadena)
    else:
        # Para los usuarios no registrados.
        html_name='buscador_anonimo.html'
        nom_usu = ""

    return render_to_response( html_name, {
        'sectiontitle': 'Página de búsqueda de servicios y usuari@s',
        'nombre_usuario': nom_usu,
        'lista_zonas': Zona.objects.all(),
        'lista_categorias': Categoria.objects.all(),
        'set_solicitado': set_solicitado,
        'servicios_buscados': servicios_buscados,
        'palabras': palabras,
        'serv_chkd': serv_chkd,
        'usu_chkd': usu_chkd,
        'ambos': ambos,
        'ofrecido': ofrecido,
        'solicitado': solicitado,
        # Pasamos los criterios de la consulta para que el usuario tenga la
        # posibilidad de simplemente modificarlos, no tener q ponerlos todos de
        # nuevo.
        'c': c,
        'z': z,
        'messages': msjs,
    })

# END buscador


@login_required
def contactar(request):
    formI = ContactoIForm()
    form = MensajeIForm()
    msj_error = ""
    if request.method == 'POST' and request.POST['id_servicio'] <> "":
        id_servicio = request.POST['id_servicio']
        servicioI = Servicio.objects.get(id=id_servicio)#Distinto de filter que siempre devuelve un queryset
        
        if servicioI.creador_id == request.user.id: #Un usuario no puede contactar consigo mismo!!!
            request.user.message_set.create(message="No puedes contactar contigo mismo!")
            #Estos es un workaround que con el otro return no haría falta
            #request2=request
            #request2.POST['palabras']=""
            #request.POST['group1']=""
            #request.POST['usu_chkd']=""
            #request.POST['serv_chkd']=""
            #request.POST['group2']
            return redirect(buscador)
        if request.POST.has_key('creaContactoI'): #Si el usuario ha decidido establecer contacto.
            if servicioI.oferta: #Si accedo a una oferta yo(request.user) soy el solicitante
                id_oferente = servicioI.creador_id
                id_solicitante = request.user.id
                ofertante_a_solicitante = False #El mensaje va de solicitante a ofertante
            else: #Si accedo a una demanda yo soy el ofertante
                id_oferente = request.user.id
                id_solicitante = servicioI.creador_id
                ofertante_a_solicitante = True
            dataContacto = { 'servicio': id_servicio,
                            'oferente': id_oferente,
                            'solicitante': id_solicitante,
                                }
            formI = ContactoIForm(dataContacto)

            if formI.is_valid():
                if len(request.POST['contenido']) > 0:
                    form = MensajeIForm(request.POST) #Para que no se borre el msj en caso de que sea demasiado largo
                    if len(request.POST['contenido']) < 400:
                        instanciaI = formI.save()
                        mandarMsj(request, instanciaI, ofertante_a_solicitante) #Mandamos el primer mensaje de la toma de contacto
                        #Además le mandamos un msj corto al usuario que ha publicado eñ servicio para que sepa del contacto
                        msjotro="El usuario: %s le ha contactado por un servicio que habia publicado. Verifiquelo en 'Conversaciones y transferencias'."%request.user.username
                        servicioI.creador.message_set.create(message=msjotro)
                        return redirect(mensajesTransf)
                        #return HttpResponseRedirect('/mensajes/') #Aquí también podríamos decir que se ha realizado la operación con éxito
                    else:
                        pass
                else:
                    msj_error = "Escriba un primer mensaje para toma de contacto con el usuario"
                
            else:
                msj_error = "Ya ha establecido contacto con este usuario por éste servicio, consulte su sección de conversaciones."
    else:
        id_servicio = ""
        servicioI = ""
        msj_error = "Lo sentimos no se ha podido establecer el contacto, vuelva a intentarlo."
    return render_to_response('contactar.html', {
                                        'sectiontitle': 'Está estableciendo contacto con un usuario para un intercambio de un servicio',
                                        'nombre_usuario': request.user.username,
                                        'form': form,
                                        'serv': servicioI,
                                        'id_servicio': id_servicio,
                                        'formI': formI,
                                        'msj_error': msj_error,
                                })


@login_required
def mensajesTransf(request):
    set_intercambios = ContactoIntercambio.objects.filter(Q(oferente=request.user)|Q(solicitante=request.user))#Todos los intercambios en los que tu estés implicado
    set_tx = Transferencia.objects.filter(Q(deudor=request.user)|Q(beneficiario=request.user)) #Todas las transferencias en las que estés implicado 
    set_tx = set_tx.filter(realizada = False)#y que no hayan sido realizadas ya(estas estarán archivadas en el historial)
    msj = ""
    if request.method == 'POST': #Si hemos decidido actuar sobre una Tx
        tx = Transferencia.objects.get(id = request.POST['id_tx'])
        #pdb.set_trace()
        if request.POST.has_key('borrar'):
            msjotro="El usuario: %s ha decidido borrar la solicitud que te habia mandado."%request.user.username
            otroTxMsj(msjotro, tx, request.user)
            tx.delete()
        elif request.POST.has_key('rechazar'):
            tx.rechazada = True
            tx.save()
            msjotro="El usuario: %s ha decidido rechazar la solicitud que le has enviado."%request.user.username
            otroTxMsj(msjotro, tx, request.user)    
        else: #Hemos decidido aceptar
            #Realizamos los cambios en las cuentas de los usuarios
            cant = float(tx.cantidad.replace(",",".")) #Convertimos float para operar

            if tx.beneficiario == request.user:
                perfB = request.user.get_profile()#Obtenemos el perfil
                perfD = tx.deudor.get_profile()
            else: #perfilBeneficiario y perfilDeudor según el caso
                perfD = request.user.get_profile()
                perfB = tx.beneficiario.get_profile()
            #Ajuste de cuentas; básicamente convertir a float, operar(restar y sumar) y reconvertir a string para que la BD lo pueda adaptar al tipo decimal
            saldoB = float(perfB.saldo) + cant #Nunca se debió usar el tipo COMMASEPARETEDINTEGERFIELD en el modelo, no da más q problemas
            saldoD = float(perfD.saldo) - cant
            #Hay que tener en cuenta que el saldo está en DecimalField y la cantidad en COMMASEPARETEDINTEGERFIELD.
            if saldoB > 10.5 or saldoD < -10.5: #Comprobamos que ninguno de los implicados sobrepase los limites establecidos.
                msj = "No puedes aceptar esta transferencia, dado que si la aceptas la cuenta de uno de los implicados quedaría en un estado incoherente: fuera del rango {-10, 10}."
            else:
                perfB.saldo = str(saldoB)
                perfD.saldo = str(saldoD)
                perfB.save()
                perfD.save()
                tx.realizada = True
                tx.save()
                msj = "La transferencia se ha realizado con éxito, verifica tu saldo y tu historial en tu página personal."
                #También un mensaje para el otro usuario
                msjotro = "Su solicitud de transferencia a:%s ha sido aceptada. Verifiquelo en su historial de servicios."%request.user.username
                otroTxMsj(msjotro, tx, request.user)    

    return render_to_response('msjTx.html', {
                                        'sectiontitle': 'Conversaciones y transferencias',
                                        'nombre_usuario': request.user.username,
                                        'usu': request.user,
                                        'set_intercambios': set_intercambios,
                                        'set_tx': set_tx,
                                        'msj': msj,
                                })


def otroTxMsj(msj, tx, usu):
    """
    Crea un mensaje al usuario pasivo(quizás no conectado) indicandole el estado de su transferencia
    que podrá ser aceptada, rechazada o borrada.
    msj: El mensaje que se le enviará al otro; tx: La transferencia; usu: El usuario activo
    """
    if tx.beneficiario == usu:
        tx.deudor.message_set.create(message=msj)
    else:
        tx.beneficiario.message_set.create(message=msj)
        
    return True


@login_required
def intercambio(request, id_inter=1):
    msj = ""
    convers_activa = True
    intercambio = ContactoIntercambio.objects.get(id=id_inter)
    servicio = Servicio.objects.get(id = intercambio.servicio_id)
    set_mensajes = MensajeI.objects.filter(contactoint = intercambio)
    boton_dis = ""
    
    if request.user.id == intercambio.solicitante.id: #Si tú eres el solicitante
        ofertante_a_solicitante = False
        if intercambio.solicitante_borrar:
            return redirect(mensajesTransf) #Hemos decidido borrar la conversación anteriormente, estos casos no deben darse sino si el usuario introduce el número del intercambio manualmente
        if intercambio.oferente_borrar:#El otro ha decidido borrar la conversación
            convers_activa = False
        
    elif request.user.id == intercambio.oferente.id:
        ofertante_a_solicitante = True
        if intercambio.oferente_borrar:
            #assert False
            return redirect(mensajesTransf)
        if intercambio.solicitante_borrar:#El otro ha decidido borra la conversación
            convers_activa = False
    else:
        return redirect(mensajesTransf)#No intervienes en el intercambio indicado y no tienes permiso para acceder.
        
    if request.method == 'POST':
        if request.POST.has_key('escribir'):#Hemos pulsado el botón de escribir
            boton_dis = "disabled"
        elif request.POST.has_key('enviar'):
            msj = mandarMsj(request, intercambio, ofertante_a_solicitante)
            #También notificación corta al otro usuario(pasivo)
            if ofertante_a_solicitante:
                msjotro = "Tiene un mensaje nuevo de: %s. Verifiquelo bajo 'Conversaciones y transferencias'."%intercambio.oferente
                intercambio.solicitante.message_set.create(message=msjotro)
                # XXX: Pablo added this
                destinatario = User.objects.get(id=intercambio.solicitante.id)
                msg_email = "Tienes un mensaje nuevo de %s que espera respuesta.\n\nAccede a la web del Banco del Tiempo del Ecolocal y consulta 'Conversaciones y transferencias'.\n\n¡No lo dejes pasar!\n\nhttp://www.ecolocal.es\n"%intercambio.oferente
                send_mail("BdT Ecolocal: Nuevo mensaje espera respuesta", msg_email, 'ecolocal@gmail.com', [destinatario.email], fail_silently=False)
            else:
                msjotro = "Tiene un mensaje nuevo de: %s. Verifiquelo bajo 'Conversaciones y transferencias'."%intercambio.solicitante
                intercambio.oferente.message_set.create(message=msjotro)
                # XXX: Pablo added this
                destinatario = User.objects.get(id=intercambio.oferente.id)
                msg_email = "Tienes un mensaje nuevo de %s que espera respuesta.\n\nAccede a la web del Banco del Tiempo del Ecolocal y consulta 'Conversaciones y transferencias'.\n\n¡No lo dejes pasar!\n\nhttp://www.ecolocal.es\n"%intercambio.solicitante
                send_mail("BdT Ecolocal: Nuevo mensaje espera respuesta", msg_email, 'ecolocal@gmail.com', [destinatario.email], fail_silently=False)
        elif request.POST.has_key('ver_menos'):
            return redirect(mensajesTransf)
        elif request.POST.has_key('atras'):
            boton_dis = ""
        elif request.POST.has_key('borrar_conv'):
            if ofertante_a_solicitante:#Si eres el ofertante
                intercambio.oferente_borrar = True
            else:
                intercambio.solicitante_borrar = True
            intercambio.save()
            return redirect(mensajesTransf)#Pues esta conversación ya no debe ser visible para el usuario.
        elif request.POST.has_key('borrar_def'):
            if not convers_activa: #Se supone que la otra parte ya ha borrado.
                intercambio.delete() #Cómo efecto de cascada se borrarán todos los mensajes dependientes de éste contacto de intercambio
                return redirect(mensajesTransf)
        elif request.POST.has_key('back'):#Ver menos con conversación inactiva
            return redirect(mensajesTransf)
        else:
            pass
        
    return render_to_response('intercambio.html', {
                                        'sectiontitle': 'Conversación sobre un intercambio',
                                        'nombre_usuario': request.user.username,
                                        'serv': servicio,
                                        'inter': intercambio,
                                        'set_mensajes': set_mensajes,
                                        'boton_dis': boton_dis,
                                        'activa': convers_activa,
                                        'msj_estado': msj,
                                })


def mandarMsj(request, intercambio, ofertante_a_solicitante):
    form = MensajeIForm({'contenido': request.POST['contenido'],})#Tb podríamos haber usado request.POST sólo,pero esto es más explicito

    if form.is_valid():#En caso de no ser válido lanza una excepción conocida y manejada. Debería...
        msj="Mensaje enviado con éxito."
        instanciaM = form.save(commit=False) #Directamente save da error de contactoint_id = 0
        instanciaM.contactoint_id = intercambio.id
        instanciaM.o_a_s = ofertante_a_solicitante
        instanciaM.save()
    else:
        msj="Mensaje demasiado largo, intente ser más breve."
        #TODO: Mostrar mensaje del formulario de error
        #for error in form.errors:
        #   msj+=str(error)
        #assert False

    return msj


@login_required 
def contAdm(request):
    msj_error =""
    cont = ""
    tema = ""
    adm = ""
    if request.method == 'POST':
        if request.POST['contenido'] == "" or request.POST['tema'] == "":
            cont = request.POST['contenido']
            tema = request.POST['tema']
            msj_error = "Por favor indique el tema y el contenido."
            
        else:
            adm = User.objects.filter(is_staff = True)[0]#La primera ocurrencia de administrador
            try:
                instancia = ContactoAdministracion.objects.create( tema = request.POST['tema'], usuario_normal = request.user, administrador = adm)#Creado nuevo contacto con la adminsitración
                MensajeA.objects.create(contactoadm = instancia, a_a_u = False, contenido = request.POST['contenido']) #Y creado primer mensaje del usuario
                return redirect(msjAdm)
                #return HttpResponseRedirect('/personal/mensajesadmin')#El usuario ya verá su conversación creada aquí
            except: #Esta excepción sólo se dará si el usuario tiene una conversación ya creada con la administración, pues sólo se puede crear una única conversación con la admin.
                msj_error = "Ya has establecido contacto con la administración, verifica tu página personal, bajo mensajes administración, sino mandanos un email."
            
            
    return render_to_response('contactoAdm.html', {
                                        'sectiontitle': 'Contacto con la administración',
                                        'nombre_usuario': request.user.username,
                                        'usu': request.user,
                                        'msj_error': msj_error,
                                        'cont': cont,
                                        'tema': tema,
                                        'adm': adm,
                                })


@login_required                             
def msjAdm(request):
    """
    Debe mostrar los mensajes con la administración y permitirnos  escribir cómo usuarios normales,
    si aún no hemos establecido contacto debe redirigirnos a la página de establecer contacto.
    """
    msj_error =""
    contacto_establecido = False
    convers_activa = True
    contacto = ""
    set_msj = ""
    
    if request.user.is_staff:#Los usuarios administradores tienen una interfaz específica para controlar la aplicación.
        msj_error = "Por favor cómo administrador debes acceder a través de la interfaz administrativa a esta sección."
    else:
        try:
            contacto = ContactoAdministracion.objects.get(usuario_normal = request.user)
            if contacto:#Si ya se ha establecido contacto.
                contacto_establecido = True
                set_msj = MensajeA.objects.filter(contactoadm = contacto)#Filtramos todos los msjs de este contacto
                if contacto.administrador_borrar:#Si el administrador ha decidido borrar la conversación
                    msj_error = "El administrador ya ha dado esta conversación por cerrada, si tiene una nueva duda. Borre la actual conversación y contactenos de nuevo."
                    convers_activa = False
                    if request.POST.has_key('borrar_def'):
                        contacto.delete()
                        return redirect(personal)
                else:
                    if request.POST.has_key('borrar_conv'):
                        contacto.usuario_borrar = True
                        contacto.save()
                    if request.POST.has_key('escribir'):
                        if request.POST['contenido'] == "":
                         msj_error = "Primero escriba un mensaje"
                        else:
                            MensajeA.objects.create(contenido = request.POST['contenido'], contactoadm = contacto, a_a_u = False)
        except:
            msj_error = "Primero establece contacto"
            
    return render_to_response('mensajesAdm.html', {
                                        'sectiontitle': 'Mensajes con la administración',
                                        'nombre_usuario': request.user.username,
                                        'usu': request.user,
                                        'msj_error': msj_error,
                                        'contacto_establecido': contacto_establecido,
                                        'contacto': contacto,
                                        'msj_error': msj_error,
                                        'set_msj': set_msj,
                                        'activa': convers_activa,
                                })
