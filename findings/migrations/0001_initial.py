# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import findings.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Artifact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=20)),
                ('value', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BaleCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(null=True, blank=True)),
                ('category_number', models.IntegerField()),
                ('parent_category', models.ForeignKey(blank=True, to='findings.BaleCategory', null=True)),
            ],
            options={
                'verbose_name_plural': 'Bale categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BusinessLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('parent', models.ForeignKey(blank=True, to='findings.BusinessLine', null=True)),
            ],
            options={
                'ordering': ['parent__name', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('comment', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=256)),
                ('file', models.FileField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('hashes', models.ManyToManyField(to='findings.Artifact', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Finding',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('is_starred', models.BooleanField(default=False)),
                ('subject', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('severity', models.IntegerField(choices=[(1, b'1'), (2, b'2'), (3, b'3'), (4, b'4')])),
                ('is_finding', models.BooleanField(default=False)),
                ('is_major', models.BooleanField(default=False)),
                ('status', models.CharField(default=b'Open', max_length=20, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'B', b'Blocked')])),
                ('confidentiality', models.IntegerField(default=b'1', choices=[(0, b'C0'), (1, b'C1'), (2, b'C2'), (3, b'C3')])),
            ],
            options={
                'permissions': (('handle_findings', 'Can handle findings'), ('view_statistics', 'Can view statistics')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FindingCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('is_major', models.BooleanField(default=False)),
                ('bale_subcategory', models.ForeignKey(to='findings.BaleCategory')),
            ],
            options={
                'verbose_name_plural': 'Finding categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FindingTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=256, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('severity', models.IntegerField(blank=True, null=True, choices=[(1, b'1'), (2, b'2'), (3, b'3'), (4, b'4')])),
                ('is_finding', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LabelGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('what', models.CharField(max_length=100, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'B', b'Blocked')])),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(blank=True, to='findings.Comments', null=True)),
                ('finding', models.ForeignKey(blank=True, to='findings.Finding', null=True)),
                ('who', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('finding_number', models.IntegerField(default=50)),
                ('hide_closed', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ValidAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('unit', models.CharField(max_length=50, null=True, blank=True)),
                ('description', models.CharField(max_length=500, null=True, blank=True)),
                ('categories', models.ManyToManyField(to='findings.FindingCategory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='label',
            name='group',
            field=models.ForeignKey(to='findings.LabelGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='findingtemplate',
            name='actor',
            field=models.ForeignKey(related_name='+', blank=True, to='findings.Label', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='findingtemplate',
            name='category',
            field=models.ForeignKey(blank=True, to='findings.FindingCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='findingtemplate',
            name='concerned_business_lines',
            field=models.ManyToManyField(to='findings.BusinessLine', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='findingtemplate',
            name='detection',
            field=models.ForeignKey(blank=True, to='findings.Label', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='findingtemplate',
            name='plan',
            field=models.ForeignKey(related_name='+', blank=True, to='findings.Label', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='finding',
            name='actor',
            field=models.ForeignKey(related_name='actor_label', blank=True, to='findings.Label', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='finding',
            name='category',
            field=models.ForeignKey(to='findings.FindingCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='finding',
            name='concerned_business_lines',
            field=models.ManyToManyField(to='findings.BusinessLine', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='finding',
            name='detection',
            field=models.ForeignKey(related_name='detection_label', to='findings.Label'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='finding',
            name='main_business_lines',
            field=models.ManyToManyField(related_name='findings_affecting_main', null=True, to='findings.BusinessLine', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='finding',
            name='opened_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='finding',
            name='plan',
            field=models.ForeignKey(related_name='plan_label', blank=True, to='findings.Label', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='file',
            name='finding',
            field=models.ForeignKey(to='findings.Finding'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comments',
            name='action',
            field=models.ForeignKey(related_name='action_label', to='findings.Label'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comments',
            name='finding',
            field=models.ForeignKey(to='findings.Finding'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comments',
            name='opened_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attribute',
            name='finding',
            field=models.ForeignKey(to='findings.Finding'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artifact',
            name='findings',
            field=models.ManyToManyField(to='findings.Finding'),
            preserve_default=True,
        ),
    ]
