# -*- coding: utf-8 -*-
import django
if django.get_version().startswith('1.5'):
    # Migração para o django 1.5 usando south

    import datetime
    from south.db import db
    from south.v2 import SchemaMigration
    from django.db import models

    class Migration(SchemaMigration):

        def forwards(self, orm):

            # Adding model 'SSOUserToken'
            db.create_table(u'innvent_sso_client_ssousertoken', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('token', self.gf('django.db.models.fields.CharField')(
                    unique=True, max_length=32)),
                ('user', self.gf('django.db.models.fields.related.OneToOneField')(
                    to=orm['auth.User'], unique=True, on_delete=models.PROTECT)),
                ('expiration_datetime', self.gf(
                    'django.db.models.fields.DateTimeField')()),
                ('last_modified', self.gf('django.db.models.fields.DateTimeField')(
                    auto_now=True, blank=True)),
            ))
            db.send_create_signal(u'innvent_sso_client', ['SSOUserToken'])

        def backwards(self, orm):

            # Deleting model 'SSOUserToken'
            db.delete_table(u'innvent_sso_client_ssousertoken')

        models = {
            u'auth.group': {
                'Meta': {'object_name': 'Group'},
                u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
                'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
                'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
            },
            u'auth.permission': {
                'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
                'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
                'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
                u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
                'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
            },
            u'auth.user': {
                'Meta': {'object_name': 'User'},
                'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 1, 19, 12, 19, 8, 593639)'}),
                'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
                'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
                'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
                u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
                'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
                'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
                'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
                'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 1, 19, 12, 19, 8, 593147)'}),
                'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
                'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
                'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
                'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
            },
            u'contenttypes.contenttype': {
                'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
                'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
                u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
                'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
                'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
            },
            u'innvent_sso_client.ssousertoken': {
                'Meta': {'object_name': 'SSOUserToken'},
                'expiration_datetime': ('django.db.models.fields.DateTimeField', [], {}),
                u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
                'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
                'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
                'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
            }
        }

        complete_apps = ['innvent_sso_client']

else:
    # Migração para o django 1.7
    from django.db import models, migrations
    from django.conf import settings

    class Migration(migrations.Migration):

        dependencies = [
            migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ]

        operations = [
            migrations.CreateModel(
                name=u'SSOUserToken',
                fields=[
                    (u'id', models.AutoField(verbose_name=u'ID',
                                             serialize=False, auto_created=True, primary_key=True)),
                    (u'token', models.CharField(unique=True, max_length=32)),
                    (u'expiration_datetime', models.DateTimeField()),
                    (u'last_modified', models.DateTimeField(auto_now=True)),
                    (u'user', models.OneToOneField(
                        to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT)),
                ],
                options={
                },
                bases=(models.Model,),
            ),
        ]