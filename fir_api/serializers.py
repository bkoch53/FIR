from django.contrib.auth.models import User
from rest_framework import serializers

from findings.models import Finding, Artifact, Label, File, FindingCategory, BusinessLine


# serializes data from the FIR User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'groups')
        read_only_fields = ('id',)
        extra_kwargs = {'url': {'view_name': 'api:user-detail'}}


# FIR Artifact model
class ArtifactSerializer(serializers.ModelSerializer):
    findings = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='api:finding-detail')

    class Meta:
        model = Artifact
        fields = ('id', 'type', 'value', 'findings')
        read_only_fields = ('id',)


# FIR File model

class AttachedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'description', 'url')
        read_only_fields = ('id',)
        extra_kwargs = {'url': {'view_name': 'api:file-detail'}}


class FileSerializer(serializers.ModelSerializer):
    finding = serializers.HyperlinkedRelatedField(read_only=True, view_name='api:finding-detail')

    class Meta:
        model = File
        fields = ('id', 'description', 'finding', 'url', 'file')
        read_only_fields = ('id',)
        extra_kwargs = {'url': {'view_name': 'api:file-download'}}
        depth = 2


# FIR Finding model

class FindingSerializer(serializers.ModelSerializer):
    detection = serializers.PrimaryKeyRelatedField(queryset=Label.objects.filter(group__name='detection'))
    actor = serializers.PrimaryKeyRelatedField(queryset=Label.objects.filter(group__name='actor'))
    plan = serializers.PrimaryKeyRelatedField(queryset=Label.objects.filter(group__name='plan'))
    file_set = AttachedFileSerializer(many=True, read_only=True)

    class Meta:
        model = Finding
        exclude = ['main_business_lines', 'artifacts']
        read_only_fields = ('id', 'opened_by', 'main_business_lines', 'file_set')
