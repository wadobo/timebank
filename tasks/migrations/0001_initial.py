# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Task'
        db.create_table('tasks_task', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('tasks', ['Task'])


    def backwards(self, orm):
        
        # Deleting model 'Task'
        db.delete_table('tasks_task')


    models = {
        'tasks.task': {
            'Meta': {'object_name': 'Task'},
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        }
    }

    complete_apps = ['tasks']
