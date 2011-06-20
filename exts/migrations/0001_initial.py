# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Extension'
        db.create_table('exts_extension', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ext_point', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('exts', ['Extension'])


    def backwards(self, orm):
        
        # Deleting model 'Extension'
        db.delete_table('exts_extension')


    models = {
        'exts.extension': {
            'Meta': {'object_name': 'Extension'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'ext_point': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['exts']
