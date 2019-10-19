# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-06 19:31
from __future__ import unicode_literals

from django.db import migrations, models
from findings.models import BusinessLine


def migrate_bls(apps, schema_editor):
    BL = apps.get_model("findings", "BusinessLine")
    db_alias = schema_editor.connection.alias

    def add_children(parent, depth):
        children = BL.objects.using(db_alias).filter(parent=parent)
        for i, child in enumerate(children):
            child.depth = depth
            child.path = BusinessLine._get_path(parent.path, depth, i+1)
            child.save()
            add_children(child, depth+1)
            parent.numchild += 1
        parent.save()
    olds = BL.objects.using(db_alias).filter(parent=None)
    for i, old in enumerate(olds):
        old.path = BusinessLine._get_path(None, 1, i+1)
        old.depth = 1
        add_children(old, 2)


def do_nothing(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('findings', '0006_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessline',
            name='depth',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='businessline',
            name='numchild',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='businessline',
            name='path',
            field=models.CharField(default='NEED_CHANGE', max_length=255, unique=False),
            preserve_default=False,
        ),
        migrations.RunPython(
            migrate_bls,
            do_nothing
        ),
        migrations.AlterField(
            model_name='businessline',
            name='path',
            field=models.CharField(default='NEED_CHANGE', max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='businessline',
            name='parent'
        ),
    ]
