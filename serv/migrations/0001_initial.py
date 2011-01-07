# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Zona'
        db.create_table('serv_zona', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre_zona', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('serv', ['Zona'])

        # Adding model 'Categoria'
        db.create_table('serv_categoria', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre_categoria', self.gf('django.db.models.fields.CharField')(max_length=45)),
        ))
        db.send_create_signal('serv', ['Categoria'])

        # Adding model 'Servicio'
        db.create_table('serv_servicio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creador', self.gf('django.db.models.fields.related.ForeignKey')(related_name='services', to=orm['user.Profile'])),
            ('oferta', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('activo', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('descripcion', self.gf('django.db.models.fields.TextField')(max_length=400)),
            ('categoria', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['serv.Categoria'])),
            ('zona', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['serv.Zona'], null=True, blank=True)),
        ))
        db.send_create_signal('serv', ['Servicio'])

        # Adding model 'ContactoIntercambio'
        db.create_table('serv_contactointercambio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('oferente', self.gf('django.db.models.fields.related.ForeignKey')(related_name='oferente', to=orm['auth.User'])),
            ('solicitante', self.gf('django.db.models.fields.related.ForeignKey')(related_name='solicitante', to=orm['auth.User'])),
            ('servicio', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tema', to=orm['serv.Servicio'])),
            ('oferente_borrar', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('solicitante_borrar', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('serv', ['ContactoIntercambio'])

        # Adding unique constraint on 'ContactoIntercambio', fields ['oferente', 'solicitante', 'servicio']
        db.create_unique('serv_contactointercambio', ['oferente_id', 'solicitante_id', 'servicio_id'])

        # Adding model 'ContactoAdministracion'
        db.create_table('serv_contactoadministracion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usuario_normal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='usuario_normal', to=orm['auth.User'])),
            ('administrador', self.gf('django.db.models.fields.related.ForeignKey')(related_name='administrador', to=orm['auth.User'])),
            ('administrador_borrar', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('usuario_borrar', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tema', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('serv', ['ContactoAdministracion'])

        # Adding unique constraint on 'ContactoAdministracion', fields ['usuario_normal', 'administrador']
        db.create_unique('serv_contactoadministracion', ['usuario_normal_id', 'administrador_id'])

        # Adding model 'MensajeI'
        db.create_table('serv_mensajei', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contenido', self.gf('django.db.models.fields.TextField')(max_length=400)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('contactoint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['serv.ContactoIntercambio'])),
            ('o_a_s', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('serv', ['MensajeI'])

        # Adding model 'MensajeA'
        db.create_table('serv_mensajea', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contenido', self.gf('django.db.models.fields.TextField')(max_length=400)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('contactoadm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['serv.ContactoAdministracion'])),
            ('a_a_u', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('serv', ['MensajeA'])

        # Adding model 'Transfer'
        db.create_table('serv_transfer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('direct_transfer_creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='direct_transfers_created', null=True, to=orm['user.Profile'])),
            ('credits_payee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transfers_received', to=orm['user.Profile'])),
            ('credits_debtor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transfers_given', to=orm['user.Profile'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='transfers', null=True, to=orm['serv.Servicio'])),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=300)),
            ('request_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('confirmation_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('credits', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('rating_votes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('rating_score', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('serv', ['Transfer'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ContactoAdministracion', fields ['usuario_normal', 'administrador']
        db.delete_unique('serv_contactoadministracion', ['usuario_normal_id', 'administrador_id'])

        # Removing unique constraint on 'ContactoIntercambio', fields ['oferente', 'solicitante', 'servicio']
        db.delete_unique('serv_contactointercambio', ['oferente_id', 'solicitante_id', 'servicio_id'])

        # Deleting model 'Zona'
        db.delete_table('serv_zona')

        # Deleting model 'Categoria'
        db.delete_table('serv_categoria')

        # Deleting model 'Servicio'
        db.delete_table('serv_servicio')

        # Deleting model 'ContactoIntercambio'
        db.delete_table('serv_contactointercambio')

        # Deleting model 'ContactoAdministracion'
        db.delete_table('serv_contactoadministracion')

        # Deleting model 'MensajeI'
        db.delete_table('serv_mensajei')

        # Deleting model 'MensajeA'
        db.delete_table('serv_mensajea')

        # Deleting model 'Transfer'
        db.delete_table('serv_transfer')


    models = {
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
        },
        'serv.categoria': {
            'Meta': {'object_name': 'Categoria'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre_categoria': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        'serv.contactoadministracion': {
            'Meta': {'unique_together': "(('usuario_normal', 'administrador'),)", 'object_name': 'ContactoAdministracion'},
            'administrador': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'administrador'", 'to': "orm['auth.User']"}),
            'administrador_borrar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tema': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'usuario_borrar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'usuario_normal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'usuario_normal'", 'to': "orm['auth.User']"})
        },
        'serv.contactointercambio': {
            'Meta': {'unique_together': "(('oferente', 'solicitante', 'servicio'),)", 'object_name': 'ContactoIntercambio'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oferente': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'oferente'", 'to': "orm['auth.User']"}),
            'oferente_borrar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'servicio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tema'", 'to': "orm['serv.Servicio']"}),
            'solicitante': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'solicitante'", 'to': "orm['auth.User']"}),
            'solicitante_borrar': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'serv.mensajea': {
            'Meta': {'object_name': 'MensajeA'},
            'a_a_u': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contactoadm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['serv.ContactoAdministracion']"}),
            'contenido': ('django.db.models.fields.TextField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'serv.mensajei': {
            'Meta': {'object_name': 'MensajeI'},
            'contactoint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['serv.ContactoIntercambio']"}),
            'contenido': ('django.db.models.fields.TextField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'o_a_s': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'serv.servicio': {
            'Meta': {'ordering': "('-pub_date',)", 'object_name': 'Servicio'},
            'activo': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'categoria': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['serv.Categoria']"}),
            'creador': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'services'", 'to': "orm['user.Profile']"}),
            'descripcion': ('django.db.models.fields.TextField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oferta': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'zona': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['serv.Zona']", 'null': 'True', 'blank': 'True'})
        },
        'serv.transfer': {
            'Meta': {'object_name': 'Transfer'},
            'confirmation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'credits': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'credits_debtor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transfers_given'", 'to': "orm['user.Profile']"}),
            'credits_payee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transfers_received'", 'to': "orm['user.Profile']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '300'}),
            'direct_transfer_creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'direct_transfers_created'", 'null': 'True', 'to': "orm['user.Profile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rating_score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'rating_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'request_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'transfers'", 'null': 'True', 'to': "orm['serv.Servicio']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'serv.zona': {
            'Meta': {'object_name': 'Zona'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre_zona': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'user.profile': {
            'Meta': {'object_name': 'Profile', '_ormbases': ['auth.User']},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'balance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '300', 'blank': 'True'}),
            'email_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'land_line': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'mobile_tlf': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['serv']
