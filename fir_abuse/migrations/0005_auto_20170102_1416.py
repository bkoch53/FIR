# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-01-02 14:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fir_abuse', '0004_auto_20170102_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abusecontact',
            name='finding_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='findings.FindingCategory'),
        ),
        migrations.AlterField(
            model_name='abusecontact',
            name='type',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
