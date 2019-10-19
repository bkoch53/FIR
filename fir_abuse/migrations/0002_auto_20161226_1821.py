# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-26 18:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('findings', '0006_merge'),
        ('fir_artifacts', '0005_delete_artifactwhitelistitem'),
        ('fir_abuse', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbuseContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('to', models.CharField(max_length=100)),
                ('cc', models.CharField(max_length=100, null=True)),
                ('bcc', models.CharField(max_length=100, null=True)),
                ('type', models.CharField(max_length=100)),
                ('finding_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='findings.FindingCategory')),
            ],
        ),
        migrations.CreateModel(
            name='AbuseTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=100)),
                ('body', models.TextField()),
                ('subject', models.TextField()),
                ('finding_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='findings.FindingCategory')),
            ],
        ),
        migrations.CreateModel(
            name='ArtifactEnrichment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=100, null=True)),
                ('name', models.CharField(max_length=100)),
                ('raw', models.TextField()),
                ('artifact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fir_artifacts.Artifact')),
            ],
        ),
        migrations.RemoveField(
            model_name='abuse',
            name='finding_category',
        ),
        migrations.DeleteModel(
            name='Abuse',
        ),
    ]
