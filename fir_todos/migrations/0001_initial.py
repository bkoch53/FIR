# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('findings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TodoItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=140)),
                ('done', models.BooleanField(default=False)),
                ('done_time', models.DateTimeField(null=True, blank=True)),
                ('deadline', models.DateField(null=True, blank=True)),
                ('business_line', models.ForeignKey(to='findings.BusinessLine')),
                ('category', models.ForeignKey(to='findings.FindingCategory')),
                ('finding', models.ForeignKey(to='findings.Finding')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
