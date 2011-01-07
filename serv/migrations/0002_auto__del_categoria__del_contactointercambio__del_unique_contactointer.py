# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'ContactoAdministracion', fields ['usuario_normal', 'administrador']
        db.delete_unique('serv_contactoadministracion', ['usuario_normal_id', 'administrador_id'])

        # Removing unique constraint on 'ContactoIntercambio', fields ['oferente', 'solicitante', 'servicio']
        db.delete_unique('serv_contactointercambio', ['oferente_id', 'solicitante_id', 'servicio_id'])

        # Removing model 'ContactoIntercambio'
        db.delete_table('serv_contactointercambio')

        # Renaming model 'Categoria'
        db.rename_column('serv_categoria', 'nombre_categoria', 'name')
        db.rename_table('serv_categoria', 'serv_category')

        # Renaming model 'Servicio'
        db.rename_column('serv_servicio', 'creador', 'creator')
        db.rename_column('serv_servicio', 'creador_id', 'creator_id')
        db.rename_column('serv_servicio', 'oferta', 'is_offer')
        db.rename_column('serv_servicio', 'activo', 'is_active')
        db.rename_column('serv_servicio', 'descripcion', 'description')
        db.rename_column('serv_servicio', 'categoria', 'category')
        db.rename_column('serv_servicio', 'categoria_id', 'category_id')
        db.rename_column('serv_servicio', 'zona', 'area')
        db.rename_column('serv_servicio', 'zona_id', 'area_id')
        db.rename_table('serv_servicio', 'serv_service')

        # Renaming model 'Zona'
        db.rename_column('serv_zona', 'nombre_zona', 'name')
        db.rename_table('serv_zona', 'serv_area')
        
        # Deleting model 'ContactoAdministracion'
        db.delete_table('serv_contactoadministracion')

        # Deleting model 'MensajeA'
        db.delete_table('serv_mensajea')

        # Deleting model 'MensajeI'
        db.delete_table('serv_mensajei')

        # Changing field 'Transfer.service'
        db.alter_column('serv_transfer', 'service_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['serv.Service']))


    def backwards(self, orm):
        # Adding model 'ContactoIntercambio'
        db.create_table('serv_contactointercambio', (
            ('servicio', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tema', to=orm['serv.Servicio'])),
            ('solicitante_borrar', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('oferente_borrar', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('oferente', self.gf('django.db.models.fields.related.ForeignKey')(related_name='oferente', to=orm['auth.User'])),
            ('solicitante', self.gf('django.db.models.fields.related.ForeignKey')(related_name='solicitante', to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('serv', ['ContactoIntercambio'])

        # Adding unique constraint on 'ContactoIntercambio', fields ['oferente', 'solicitante', 'servicio']
        db.create_unique('serv_contactointercambio', ['oferente_id', 'solicitante_id', 'servicio_id'])

        # Adding model 'ContactoAdministracion'
        db.create_table('serv_contactoadministracion', (
            ('usuario_normal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='usuario_normal', to=orm['auth.User'])),
            ('usuario_borrar', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('administrador', self.gf('django.db.models.fields.related.ForeignKey')(related_name='administrador', to=orm['auth.User'])),
            ('tema', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('administrador_borrar', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('serv', ['ContactoAdministracion'])

        # Adding unique constraint on 'ContactoAdministracion', fields ['usuario_normal', 'administrador']
        db.create_unique('serv_contactoadministracion', ['usuario_normal_id', 'administrador_id'])

        # Adding model 'MensajeA'
        db.create_table('serv_mensajea', (
            ('contactoadm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['serv.ContactoAdministracion'])),
            ('contenido', self.gf('django.db.models.fields.TextField')(max_length=400)),
            ('a_a_u', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('serv', ['MensajeA'])

        # Adding model 'MensajeI'
        db.create_table('serv_mensajei', (
            ('contactoint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['serv.ContactoIntercambio'])),
            ('contenido', self.gf('django.db.models.fields.TextField')(max_length=400)),
            ('o_a_s', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('serv', ['MensajeI'])

        # Renaming model 'Categoria'
        db.rename_column('serv_category', 'name', 'nombre_categoria')
        db.rename_table('serv_category', 'serv_categoria')

        # Renaming model 'Servicio'
        db.rename_column('serv_service', 'creator', 'creador')
        db.rename_column('serv_service', 'creator_id', 'creador_id')
        db.rename_column('serv_service', 'is_offer', 'oferta')
        db.rename_column('serv_service', 'is_active', 'activo')
        db.rename_column('serv_service', 'description', 'descripcion')
        db.rename_column('serv_service', 'category', 'categoria')
        db.rename_column('serv_service', 'category_id', 'categoria_id')
        db.rename_column('serv_service', 'area', 'zona')
        db.rename_column('serv_service', 'area_id', 'zona_id')
        db.rename_table('serv_service', 'serv_servicio')

        # Renaming model 'Zona'
        db.rename_column('serv_area', 'name', 'nombre_zona')
        db.rename_table('serv_area', 'serv_zona')

        # Changing field 'Transfer.service'
        db.alter_column('serv_transfer', 'service_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['serv.Servicio']))


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
        'serv.area': {
            'Meta': {'object_name': 'Area'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'serv.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        'serv.service': {
            'Meta': {'ordering': "('-pub_date',)", 'object_name': 'Service'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['serv.Area']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['serv.Category']"}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'services'", 'to': "orm['user.Profile']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_offer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
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
            'service': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'transfers'", 'null': 'True', 'to': "orm['serv.Service']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'})
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
