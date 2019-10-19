# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-16 12:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('findings', '0006_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Abuse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=100)),
                ('body', models.TextField()),
                ('subject', models.TextField()),
                ('finding_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='findings.FindingCategory')),
            ],
            options={
                'db_table': 'findings_abuse',
            },
        ),
    ]
