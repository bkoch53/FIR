from django.db import models
from django import forms

from findings.models import FindingCategory


class AbuseTemplate(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, blank=True)
    body = models.TextField()
    subject = models.TextField()
    finding_category = models.ForeignKey(FindingCategory, blank=True, null=True)

    def __unicode__(self):
        return self.name


class AbuseContact(models.Model):
    name = models.CharField(max_length=100)
    to = models.CharField(max_length=100)
    cc = models.CharField(max_length=100, blank=True)
    bcc = models.CharField(max_length=100, blank=True)
    finding_category = models.ForeignKey(FindingCategory, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.name


class EmailForm(forms.Form):
    behalf = forms.CharField()
    to = forms.CharField()
    cc = forms.CharField()
    bcc = forms.CharField()
    subject = forms.CharField()
    body = forms.CharField(widget=forms.Textarea)
