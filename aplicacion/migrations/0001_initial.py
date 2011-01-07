# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PerfilUsuario'
        db.create_table('aplicacion_perfilusuario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Perfil de usuario', unique=True, to=orm['auth.User'])),
            ('fecha_de_nacimiento', self.gf('django.db.models.fields.DateField')()),
            ('direccion', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('saldo', self.gf('django.db.models.fields.DecimalField')(default=0, max_length=4, max_digits=3, decimal_places=1)),
            ('descr', self.gf('django.db.models.fields.TextField')(max_length=150, blank=True)),
            ('puntGlob', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(default=22, max_length=4)),
        ))
        db.send_create_signal('aplicacion', ['PerfilUsuario'])

        # Adding model 'Comentario'
        db.create_table('aplicacion_comentario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('autor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='autor', to=orm['auth.User'])),
            ('destinatario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='destinatario', to=orm['auth.User'])),
            ('contenido', self.gf('django.db.models.fields.TextField')(max_length=200)),
            ('puntuacion', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=4)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('aplicacion', ['Comentario'])

        # Adding model 'Transferencia'
        db.create_table('aplicacion_transferencia', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('beneficiario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='beneficiario', to=orm['auth.User'])),
            ('deudor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deudor', to=orm['auth.User'])),
            ('creoBeneficiario', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('descrServ', self.gf('django.db.models.fields.TextField')(max_length=40)),
            ('fechaTx', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('realizada', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('rechazada', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cantidad', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=3)),
        ))
        db.send_create_signal('aplicacion', ['Transferencia'])


    def backwards(self, orm):
        
        # Deleting model 'PerfilUsuario'
        db.delete_table('aplicacion_perfilusuario')

        # Deleting model 'Comentario'
        db.delete_table('aplicacion_comentario')

        # Deleting model 'Transferencia'
        db.delete_table('aplicacion_transferencia')


    models = {
        'aplicacion.comentario': {
            'Meta': {'object_name': 'Comentario'},
            'autor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'autor'", 'to': "orm['auth.User']"}),
            'contenido': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            'destinatario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'destinatario'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'puntuacion': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '4'})
        },
        'aplicacion.perfilusuario': {
            'Meta': {'object_name': 'PerfilUsuario'},
            'descr': ('django.db.models.fields.TextField', [], {'max_length': '150', 'blank': 'True'}),
            'direccion': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'fecha_de_nacimiento': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'puntGlob': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'default': '22', 'max_length': '4'}),
            'saldo': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_length': '4', 'max_digits': '3', 'decimal_places': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Perfil de usuario'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'aplicacion.transferencia': {
            'Meta': {'object_name': 'Transferencia'},
            'beneficiario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'beneficiario'", 'to': "orm['auth.User']"}),
            'cantidad': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '3'}),
            'creoBeneficiario': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'descrServ': ('django.db.models.fields.TextField', [], {'max_length': '40'}),
            'deudor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deudor'", 'to': "orm['auth.User']"}),
            'fechaTx': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'realizada': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rechazada': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['aplicacion']
