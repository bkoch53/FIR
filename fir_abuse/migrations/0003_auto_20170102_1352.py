# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-01-02 13:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fir_abuse', '0002_auto_20161226_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abusetemplate',
            name='finding_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='findings.FindingCategory'),
        ),
        migrations.AlterField(
            model_name='abusetemplate',
            name='type',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
