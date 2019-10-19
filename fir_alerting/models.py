from django.db import models
from django import forms

from findings.models import FindingCategory, BusinessLine


class RecipientTemplate(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    behalf = models.CharField(max_length=100)
    recipient_to = models.TextField()
    recipient_cc = models.TextField()
    recipient_bcc = models.TextField(null=True, blank=True)
    business_line = models.ForeignKey(BusinessLine, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'findings_recipienttemplate'


class CategoryTemplate(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    body = models.TextField(help_text="This is a Markdown field. You can use django templating language.")
    subject = models.TextField()
    finding_category = models.ForeignKey(FindingCategory)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'findings_categorytemplate'


class EmailForm(forms.Form):
    behalf = forms.CharField()
    to = forms.CharField()
    cc = forms.CharField()
    bcc = forms.CharField()
    subject = forms.CharField()
    body = forms.CharField(widget=forms.Textarea)
