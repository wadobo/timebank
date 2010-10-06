

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


from serv.models import Servicio, ContactoIntercambio, MensajeI
from django import forms


class ServicioForm(forms.ModelForm):

    OFERTA_CHOICES = (
        ('0', 'DEMANDA'),
        ('1', 'OFERTA'),
    )

    oferta = forms.CharField(label="Crear una",
                             help_text=", debe elegir si es una oferta "
                                       "(ofrece algo) o una demanda(solicita "
                                       "algo)",
                             widget=forms.Select(choices=OFERTA_CHOICES))

    class Meta:
        model = Servicio
        exclude = ('creador', 'pub_date', 'activo')

    def clean_oferta(self):
        oferta = self.cleaned_data.get("oferta", "0")
        if int(oferta):
            oferta = 1
        else:
            oferta = 0

        return oferta

    def clean_descripcion(self):
        descr = self.cleaned_data.get("descripcion", "")
        if len(descr) > 400:
            raise forms.ValidationError("La descripcion no debe pasar de "
                                        "400caracteres, la actual tiene %s" %
                                        len(descr))
        return descr


class ContactoIForm(forms.ModelForm):

    class Meta:
        model = ContactoIntercambio


class MensajeIForm(forms.ModelForm):

    class Meta:
        model = MensajeI
        fields = ['contenido']

    def clean_contenido(self):
        conte = self.cleaned_data.get("contenido", "")
        if 1 > len(conte) or len(conte) > 400:
            raise forms.ValidationError("El comentario debe tener entre 1 "
                                        "y 400 caracteres y el actual tiene "
                                        "%s." % len(conte))
        return conte
