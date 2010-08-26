# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TextProcessor'
        db.create_table('djangomarkup_textprocessor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('function', self.gf('django.db.models.fields.CharField')(unique=True, max_length=96)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=96, blank=True)),
            ('processor_options', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('djangomarkup', ['TextProcessor'])

        # Adding model 'SourceText'
        db.create_table('djangomarkup_sourcetext', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('processor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangomarkup.TextProcessor'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('modification_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('djangomarkup', ['SourceText'])

        # Adding unique constraint on 'SourceText', fields ['content_type', 'object_id', 'field']
        db.create_unique('djangomarkup_sourcetext', ['content_type_id', 'object_id', 'field'])


    def backwards(self, orm):
        
        # Deleting model 'TextProcessor'
        db.delete_table('djangomarkup_textprocessor')

        # Deleting model 'SourceText'
        db.delete_table('djangomarkup_sourcetext')

        # Removing unique constraint on 'SourceText', fields ['content_type', 'object_id', 'field']
        db.delete_unique('djangomarkup_sourcetext', ['content_type_id', 'object_id', 'field'])


    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djangomarkup.sourcetext': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'field'),)", 'object_name': 'SourceText'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modification_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'processor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangomarkup.TextProcessor']"})
        },
        'djangomarkup.textprocessor': {
            'Meta': {'object_name': 'TextProcessor'},
            'function': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '96'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '96', 'blank': 'True'}),
            'processor_options': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['djangomarkup']
