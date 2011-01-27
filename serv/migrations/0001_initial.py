# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Area'
        db.create_table('serv_area', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('serv', ['Area'])

        # Adding model 'Category'
        db.create_table('serv_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45)),
        ))
        db.send_create_signal('serv', ['Category'])

        # Adding model 'Service'
        db.create_table('serv_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='services', to=orm['user.Profile'])),
            ('is_offer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=400)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['serv.Category'])),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['serv.Area'], null=True, blank=True)),
        ))
        db.send_create_signal('serv', ['Service'])

        # Adding model 'Transfer'
        db.create_table('serv_transfer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('direct_transfer_creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='direct_transfers_created', null=True, to=orm['user.Profile'])),
            ('credits_payee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transfers_received', to=orm['user.Profile'])),
            ('credits_debtor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transfers_given', to=orm['user.Profile'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='transfers', null=True, to=orm['serv.Service'])),
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
        
        # Deleting model 'Area'
        db.delete_table('serv_area')

        # Deleting model 'Category'
        db.delete_table('serv_category')

        # Deleting model 'Service'
        db.delete_table('serv_service')

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
