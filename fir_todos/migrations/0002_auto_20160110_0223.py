# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('findings', '0002_auto_20150907_1147'),
        ('fir_todos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TodoListTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('category', models.ForeignKey(blank=True, to='findings.FindingCategory', null=True)),
                ('concerned_business_lines', models.ManyToManyField(to='findings.BusinessLine', null=True, blank=True)),
                ('detection', models.ForeignKey(blank=True, to='findings.Label', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='finding',
            field=models.ForeignKey(blank=True, to='findings.Finding', null=True),
            preserve_default=True,
        ),
    ]
