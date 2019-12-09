from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from fir_notifications.decorators import notification_observation

from fir_notifications.registry import registry
from findings.models import model_created, Finding, model_updated, Comments, model_status_changed


@python_2_unicode_compatible
class MethodConfiguration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='method_preferences', verbose_name=_('user'))
    key = models.CharField(max_length=60, choices=registry.get_method_choices(), verbose_name=_('method'))
    value = models.TextField(verbose_name=_('configuration'))

    def __str__(self):
        return "{user}: {method} configuration".format(user=self.user, method=self.key)

    class Meta:
        verbose_name = _('method configuration')
        verbose_name_plural = _('method configurations')
        unique_together = (("user", "key"),)
        index_together = ["user", "key"]


class NotificationTemplate(models.Model):
    observation = models.CharField(max_length=60, choices=registry.get_observation_choices(), verbose_name=_('observation'))
    business_lines = models.ManyToManyField('findings.BusinessLine', related_name='+', blank=True,
                                            verbose_name=_('business line'))
    subject = models.CharField(max_length=200, blank=True, default="", verbose_name=_('subject'))
    short_description = models.TextField(blank=True, default="", verbose_name=_('short description'))
    description = models.TextField(blank=True, default="", verbose_name=_('description'))

    class Meta:
        verbose_name = _('notification template')
        verbose_name_plural = _('notification templates')


@python_2_unicode_compatible
class NotificationPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notification_preferences', verbose_name=_('user'))
    observation = models.CharField(max_length=60, verbose_name=_('observation'))
    method = models.CharField(max_length=60, verbose_name=_('method'))
    business_lines = models.ManyToManyField('findings.BusinessLine', related_name='+', blank=True,
                                            verbose_name=_('business lines'))

    def __str__(self):
        return "{user}: {observation} notification preference for {method}".format(user=self.user,
                                                                             observation=self.observation,
                                                                             method=self.method)

    class Meta:
        verbose_name = _('notification preference')
        verbose_name_plural = _('notification preferences')
        unique_together = (("user", "observation", "method"),)
        index_together = ["user", "observation", "method"]
        ordering = ['user', 'observation', 'method']


if not settings.NOTIFICATIONS_MERGE_FINDINGS_AND_OBSERVATIONS:
    @notification_observation('observation:created', model_created, Finding, verbose_name=_('Observation created'),
                        section=_('Observation'))
    def observation_created(sender, instance, **kwargs):
        if instance.is_finding:
            return None, None
        return instance, instance.concerned_business_lines


    @notification_observation('observation:updated', model_updated, Finding, verbose_name=_('Observation updated'),
                        section=_('Observation'))
    def observation_updated(sender, instance, **kwargs):
        if instance.is_finding:
            return None, None
        return instance, instance.concerned_business_lines


    @notification_observation('observation:commented', post_save, Comments, verbose_name=_('Observation commented'),
                        section=_('Observation'))
    def observation_commented(sender, instance, **kwargs):
        if not instance.finding and instance.finding.is_finding:
            return None, None
        if instance.action.name in ['Opened', 'Blocked', 'Closed']:
            return None, None
        return instance, instance.finding.concerned_business_lines


    @notification_observation('observation:status_changed', model_status_changed, Finding, verbose_name=_('Observation status changed'),
                        section=_('Observation'))
    def observation_status_changed(sender, instance, **kwargs):
        if instance.is_finding:
            return None, None
        return instance, instance.concerned_business_lines


@notification_observation('finding:created', model_created, Finding, verbose_name=_('Finding created'),
                    section=_('Finding'))
def finding_created(sender, instance, **kwargs):
    if not instance.is_finding:
        return None, None
    return instance, instance.concerned_business_lines


@notification_observation('finding:updated', model_updated, Finding, verbose_name=_('Finding updated'),
                    section=_('Finding'))
def finding_updated(sender, instance, **kwargs):
    if not settings.NOTIFICATIONS_MERGE_FINDINGS_AND_OBSERVATIONS and not instance.is_finding:
        return None, None
    return instance, instance.concerned_business_lines


@notification_observation('finding:commented', post_save, Comments, verbose_name=_('Finding commented'),
                    section=_('Finding'))
def finding_commented(sender, instance, **kwargs):
    if not instance.finding and not settings.NOTIFICATIONS_MERGE_FINDINGS_AND_OBSERVATIONS and not instance.finding.is_finding:
        return None, None
    if instance.action.name in ['Opened', 'Blocked', 'Closed']:
        return None, None
    return instance, instance.finding.concerned_business_lines


@notification_observation('finding:status_changed', model_status_changed, Finding, verbose_name=_('Finding status changed'),
                    section=_('Finding'))
def finding_status_changed(sender, instance, **kwargs):
    if not settings.NOTIFICATIONS_MERGE_FINDINGS_AND_OBSERVATIONS and not instance.is_finding:
        return None, None
    return instance, instance.concerned_business_lines
