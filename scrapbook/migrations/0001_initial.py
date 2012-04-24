# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Checkin'
        db.create_table('scrapbook_checkin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('checkin_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('venue_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('scrapbook', ['Checkin'])

        # Adding model 'Entry'
        db.create_table('scrapbook_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('checkin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scrapbook.Checkin'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('scrapbook', ['Entry'])

        # Adding model 'Photo'
        db.create_table('scrapbook_photo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scrapbook.Entry'])),
            ('image', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('scrapbook', ['Photo'])

    def backwards(self, orm):
        # Deleting model 'Checkin'
        db.delete_table('scrapbook_checkin')

        # Deleting model 'Entry'
        db.delete_table('scrapbook_entry')

        # Deleting model 'Photo'
        db.delete_table('scrapbook_photo')

    models = {
        'scrapbook.checkin': {
            'Meta': {'object_name': 'Checkin'},
            'checkin_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'venue_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'scrapbook.entry': {
            'Meta': {'object_name': 'Entry'},
            'checkin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scrapbook.Checkin']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'scrapbook.photo': {
            'Meta': {'object_name': 'Photo'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scrapbook.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['scrapbook']