# -*- coding: utf-8 -*-
import datetime

from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from treebeard.mp_tree import MP_Node

from fir_artifacts import artifacts
from fir_artifacts.models import Artifact, File
from fir_plugins.models import link_to
from findings.authorization import tree_authorization, AuthorizationModelMixin

STATUS_CHOICES = (
    ("O", _("Open")),
    ("C", _("Closed")),
    ("B", _("Blocked")),
)

SEVERITY_CHOICES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
)

LOG_ACTIONS = (
    ("D", "Deleted"),
    ("C", "Created"),
    ("U", "Update"),
    ("LI", "Logged in"),
    ("LO", "Logged out"),
)

CONFIDENTIALITY_LEVEL = (
    (0, "C0"),
    (1, "C1"),
    (2, "C2"),
    (3, "C3"),
)

# Special Model class that handles signals


model_created = Signal(providing_args=['instance'])
model_updated = Signal(providing_args=['instance'])
model_status_changed = Signal(providing_args=['instance', 'previous_status'])


class FIRModel:
    def done_creating(self):
        model_created.send(sender=self.__class__, instance=self)

    def done_updating(self):
        model_updated.send(sender=self.__class__, instance=self)


# Profile ====================================================================


class Profile(models.Model):
    user = models.OneToOneField(User)
    finding_number = models.IntegerField(default=50)
    hide_closed = models.BooleanField(default=False)

    def __unicode__(self):
        return u"Profile for user '{}'".format(self.user)


# Audit trail ================================================================


class Log(models.Model):
    who = models.ForeignKey(User, null=True, blank=True)
    what = models.CharField(max_length=100, choices=STATUS_CHOICES)
    when = models.DateTimeField(auto_now_add=True)
    finding = models.ForeignKey('Finding', null=True, blank=True)
    comment = models.ForeignKey('Comments', null=True, blank=True)

    def __unicode__(self):
        if self.finding:
            return u"[%s] %s %s (%s)" % (self.when, self.what, self.finding, self.who)
        elif self.comment:
            return u"[%s] %s comment on %s (%s)" % (self.when, self.what, self.comment.finding, self.who)
        else:
            return u"[%s] %s (%s)" % (self.when, self.what, self.who)


class LabelGroup(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=50)
    group = models.ForeignKey(LabelGroup)

    def __unicode__(self):
        return "%s" % (self.name)


class BusinessLine(MP_Node, AuthorizationModelMixin):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        parents = list(self.get_ancestors())
        parents.append(self)
        return u" > ".join([bl.name for bl in parents])

    class Meta:
        verbose_name = _('business line')

    def get_finding_count(self, query):
        finding_count = self.finding_set.filter(query).distinct().count()
        finding_count += Finding.objects.filter(query).filter(
            concerned_business_lines__in=self.get_descendants()).distinct().count()
        return finding_count


class AccessControlEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    business_line = models.ForeignKey(BusinessLine, verbose_name=_('business line'), related_name='acl')
    role = models.ForeignKey('auth.Group', verbose_name=_('role'))

    def __unicode__(self):
        return _("{} is {} on {}").format(self.user, self.role, self.business_line)

    class Meta:
        verbose_name = _('access control entry')
        verbose_name_plural = _('access control entries')


class BaleCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category_number = models.IntegerField()
    parent_category = models.ForeignKey('BaleCategory', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Bale categories"

    def __unicode__(self):
        if self.parent_category:
            return "(%s > %s) %s" % (self.parent_category.category_number, self.category_number, self.name)
        else:
            return "(%s) %s" % (self.category_number, self.name)


class FindingCategory(models.Model):
    name = models.CharField(max_length=100)
    bale_subcategory = models.ForeignKey(BaleCategory)
    is_major = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Finding categories"

    def __unicode__(self):
        return self.name


# Core models ================================================================

@tree_authorization(fields=['concerned_business_lines', ], tree_model='findings.BusinessLine',
                    owner_field='opened_by', owner_permission=settings.FINDING_CREATOR_PERMISSION)
@link_to(File)
@link_to(Artifact)
class Finding(FIRModel, models.Model):
    date = models.DateTimeField(default=datetime.datetime.now, blank=True)
    is_starred = models.BooleanField(default=False)
    subject = models.CharField(max_length=256)
    description = models.TextField()
    category = models.ForeignKey(FindingCategory)
    concerned_business_lines = models.ManyToManyField(BusinessLine, blank=True)
    main_business_lines = models.ManyToManyField(BusinessLine, related_name='findings_affecting_main', blank=True)
    detection = models.ForeignKey(Label, limit_choices_to={'group__name': 'detection'}, related_name='detection_label')
    severity = models.IntegerField(choices=SEVERITY_CHOICES)
    is_finding = models.BooleanField(default=False)
    is_major = models.BooleanField(default=False)
    actor = models.ForeignKey(Label, limit_choices_to={'group__name': 'actor'}, related_name='actor_label', blank=True,
                              null=True)
    plan = models.ForeignKey(Label, limit_choices_to={'group__name': 'plan'}, related_name='plan_label', blank=True,
                             null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=_("Open"))
    opened_by = models.ForeignKey(User)
    confidentiality = models.IntegerField(choices=CONFIDENTIALITY_LEVEL, default='1')

    def __unicode__(self):
        return self.subject

    def is_open(self):
        return self.get_last_action != "Closed"

    def close_timeout(self):
        previous_status = self.status
        self.status = 'C'
        self.save()
        model_status_changed.send(sender=Finding, instance=self, previous_status=previous_status)

        c = Comments()
        c.comment = "Finding closed (timeout)"
        c.date = datetime.datetime.now()
        c.action = Label.objects.get(name='Closed', group__name='action')
        c.finding = self
        c.opened_by = User.objects.get(username='cert')
        c.save()

    def get_last_comment(self):
        return self.comments_set.order_by('-date')[0]

    def get_last_action(self):
        c = self.comments_set.order_by('-date')[0]

        action = "%s (%s)" % (c.action, c.date.strftime("%Y %d %b %H:%M:%S"))

        return action

    def concerns_business_line(self, bl_string):
        for bl in self.concerned_business_lines.all():
            if bl.name == bl_string:
                return bl.name
            if bl.get_ancestors().filter(name=bl_string).count():
                return bl.name
        return False

    def get_business_lines_names(self):
        return ", ".join([b.name for b in self.concerned_business_lines.all()])

    def refresh_main_business_lines(self):
        mainbls = set()
        for bl in self.concerned_business_lines.all():
            mainbls.add(bl.get_root())
        self.main_business_lines = list(mainbls)

    def refresh_artifacts(self, data=""):
        if data == "":
            coms = self.comments_set.all()

            data = self.description
            for c in coms:
                data += "\n" + c.comment

        found_artifacts = artifacts.find(data)

        artifact_list = []
        for key in found_artifacts:
            for a in found_artifacts[key]:
                artifact_list.append((key, a))

        db_artifacts = Artifact.objects.filter(value__in=[a[1] for a in artifact_list])

        exist = []

        for a in db_artifacts:
            exist.append((a.type, a.value))
            if self not in a.findings.all():
                a.findings.add(self)

        new_artifacts = list(set(artifact_list) - set(exist))
        all_artifacts = list(set(artifact_list))

        for a in new_artifacts:
            new = Artifact(type=a[0], value=a[1])
            new.save()
            new.findings.add(self)

        for a in all_artifacts:
            artifacts.after_save(a[0], a[1], self)

    class Meta:
        permissions = (
            ('handle_findings', 'Can handle findings'),
            ('report_observations', 'Can report observations'),
            ('view_findings', 'Can view findings'),
            ('view_statistics', 'Can view statistics'),
        )


class Comments(models.Model):
    date = models.DateTimeField(default=datetime.datetime.now, blank=True)
    comment = models.TextField()
    action = models.ForeignKey(Label, limit_choices_to={'group__name': 'action'}, related_name='action_label')
    finding = models.ForeignKey(Finding)
    opened_by = models.ForeignKey(User)

    class Meta:
        verbose_name_plural = 'comments'

    def __unicode__(self):
        return u"Comment for finding %s" % self.finding.id

    @classmethod
    def create_diff_comment(cls, finding, data, user):
        comments = ''
        for key in data:
            # skip the following fields from diff
            if key in ['description', 'concerned_business_lines', 'main_business_lines']:
                continue

            new = data[key]
            old = getattr(finding, key)

            if new != old:
                label = key

                if key == 'is_major':
                    label = 'major'
                if key == 'concerned_business_lines':
                    label = "business lines"
                if key == 'main_business_line':
                    label = "main business line"
                if key == 'is_finding':
                    label = 'finding'

                if old == "O":
                    old = 'Open'
                if old == "C":
                    old = 'Closed'
                if old == "B":
                    old = 'Blocked'
                if new == "O":
                    new = 'Open'
                if new == "C":
                    new = 'Closed'
                if new == "B":
                    new = 'Blocked'

                comments += u'Changed "%s" from "%s" to "%s"; ' % (label, old, new)

        if comments:
            Comments.objects.create(
                comment=comments,
                action=Label.objects.get(name='Info'),
                finding=finding,
                opened_by=user
            )


class Attribute(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=200)
    finding = models.ForeignKey(Finding)

    def __unicode__(self):
        return "%s: %s" % (self.name, self.value)


class ValidAttribute(models.Model):
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    categories = models.ManyToManyField(FindingCategory)

    def __unicode__(self):
        return self.name


# Templating =================================================================

class FindingTemplate(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(FindingCategory, null=True, blank=True)
    concerned_business_lines = models.ManyToManyField(BusinessLine, blank=True)
    detection = models.ForeignKey(Label, limit_choices_to={'group__name': 'detection'}, null=True, blank=True)
    severity = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True)
    is_finding = models.BooleanField(default=False)
    actor = models.ForeignKey(Label, limit_choices_to={'group__name': 'actor'}, related_name='+', blank=True, null=True)
    plan = models.ForeignKey(Label, limit_choices_to={'group__name': 'plan'}, related_name='+', blank=True, null=True)

    def __unicode__(self):
        return self.name


#
# Signal receivers
#


@receiver(model_created, sender=Finding)
@receiver(model_updated, sender=Finding)
def refresh_finding(sender, instance, **kwargs):
    instance.refresh_artifacts(instance.description)


# Automatically create comments


@receiver(post_save, sender=Finding)
def comment_new_finding(sender, instance, created, **kwargs):
    if created:
        Comments.objects.create(
            comment='Finding opened',
            action=Label.objects.get(name='Opened'),
            finding=instance,
            opened_by=instance.opened_by,
            date=instance.date,
        )


# Automatically log actions


@receiver(post_save, sender=Finding)
def log_new_finding(sender, instance, created, **kwargs):
    if created:
        what = 'Created finding'
    else:
        what = 'Edit finding'

    Log.objects.create(who=instance.opened_by, what=what, finding=instance)
