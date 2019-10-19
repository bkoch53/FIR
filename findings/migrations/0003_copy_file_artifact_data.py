# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.contenttypes.models import ContentType

def migrate_artifacts(apps, schema_editor):
    Artifact = apps.get_model("fir_artifacts", "Artifact")
    FindingsArtifact = apps.get_model("findings", "Artifact")
    db_alias = schema_editor.connection.alias
    olds = FindingsArtifact.objects.using(db_alias).all()
    for old in olds:
        artifact = Artifact.objects.using(db_alias).create(id=old.id,type=old.type, value=old.value)
        for finding in old.findings.all():
            artifact.findings.add(finding)

def migrate_files(apps, schema_editor):
    File = apps.get_model("fir_artifacts", "File")
    FindingsFile = apps.get_model("findings", "File")
    Findings = apps.get_model("findings", "Finding")
    Artifact = apps.get_model("fir_artifacts", "Artifact")
    db_alias = schema_editor.connection.alias
    olds = FindingsFile.objects.using(db_alias).all()
    finding_type = ContentType.objects.get_for_model(Findings)
    for old in olds:
        file = File.objects.using(db_alias).create(id=old.id,description=old.description, date=old.date, file=old.file)
        file.content_type_id = finding_type.pk
        file.object_id = old.finding.pk
        file.save()
        for old_hash in old.hashes.all():
            new_hash = Artifact.objects.using(db_alias).get(pk=old_hash.pk)
            file.hashes.add(new_hash)



class Migration(migrations.Migration):

    dependencies = [
        ('findings', '0002_link_findings_to_artifacts'),
        ('fir_artifacts', '0002_create_artifacts'),
    ]

    operations = [
        migrations.RunPython(
            migrate_artifacts,
        ),
        migrations.RunPython(
            migrate_files, atomic=False
        ),
    ]
