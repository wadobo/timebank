# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('photo', models.ImageField(upload_to=b'/home/danigm/Projects/work/timebank/site_media/photos', null=True, verbose_name='Avatar', blank=True)),
                ('birth_date', models.DateField(default=datetime.date(2015, 3, 26), verbose_name='Birth date')),
                ('address', models.CharField(default='address', max_length=100, verbose_name='Address')),
                ('balance', models.IntegerField(default=0)),
                ('description', models.TextField(max_length=300, verbose_name='Personal address', blank=True)),
                ('land_line', models.CharField(max_length=20, verbose_name='Land line')),
                ('mobile_tlf', models.CharField(max_length=20, verbose_name='Mobile phone')),
                ('email_updates', models.BooleanField(default=True, verbose_name='Receive email updates')),
                ('lang_code', models.CharField(default=b'', max_length=10, verbose_name='Language Code')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            bases=('auth.user',),
        ),
    ]
