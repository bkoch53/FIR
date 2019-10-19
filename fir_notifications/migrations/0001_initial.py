# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-01-14 13:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('findings', '0009_add_finding_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='MethodConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=60, verbose_name='method')),
                ('value', models.TextField(verbose_name='configuration')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='method_preferences', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'method configuration',
                'verbose_name_plural': 'method configurations',
            },
        ),
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observation', models.CharField(max_length=60, verbose_name='observation')),
                ('subject', models.CharField(blank=True, default='', max_length=200, verbose_name='subject')),
                ('short_description', models.TextField(blank=True, default='', verbose_name='short description')),
                ('description', models.TextField(blank=True, default='', verbose_name='description')),
                ('business_lines', models.ManyToManyField(blank=True, related_name='_notificationtemplate_business_lines_+', to='findings.BusinessLine', verbose_name='business line')),
            ],
            options={
                'verbose_name': 'notification template',
                'verbose_name_plural': 'notification templates',
            },
        ),
        migrations.AlterUniqueTogether(
            name='methodconfiguration',
            unique_together=set([('user', 'key')]),
        ),
        migrations.AlterIndexTogether(
            name='methodconfiguration',
            index_together=set([('user', 'key')]),
        ),
    ]
