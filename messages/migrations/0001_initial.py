# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Message'
        db.create_table('messages_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_messages', to=orm['auth.User'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='received_messages', null=True, to=orm['auth.User'])),
            ('parent_msg', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='next_messages', null=True, to=orm['messages.Message'])),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('read_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('replied_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('sender_deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('recipient_deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='messages', null=True, to=orm['serv.Servicio'])),
            ('transfer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='messages', null=True, to=orm['serv.Transfer'])),
        ))
        db.send_create_signal('messages', ['Message'])


    def backwards(self, orm):
        
        # Deleting model 'Message'
        db.delete_table('messages_message')


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
        'messages.message': {
            'Meta': {'ordering': "['-sent_at']", 'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parent_msg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'next_messages'", 'null': 'True', 'to': "orm['messages.Message']"}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'received_messages'", 'null': 'True', 'to': "orm['auth.User']"}),
            'recipient_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'replied_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': "orm['auth.User']"}),
            'sender_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'messages'", 'null': 'True', 'to': "orm['serv.Servicio']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'transfer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'messages'", 'null': 'True', 'to': "orm['serv.Transfer']"})
        },
        'serv.categoria': {
            'Meta': {'object_name': 'Categoria'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre_categoria': ('django.db.models.fields.CharField', [], {'max_length': '45'})
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

    complete_apps = ['messages']
