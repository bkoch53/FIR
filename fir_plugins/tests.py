from django.test import TestCase
from fir_plugins.models import ManyLinkableModel, OneLinkableModel, link_to

from django.db import models


class OneLinked(OneLinkableModel):
    name = models.CharField(max_length=100)


@link_to(OneLinked)
class FileHolder(OneLinkableModel):
    name = models.CharField(max_length=100)


class Finding(models.Model):
    name = models.CharField(max_length=100)


class NotRelatedModel(models.Model):
    name = models.CharField(max_length=100)


class Artifact(ManyLinkableModel):
    name = models.CharField(max_length=100)


@link_to(Artifact)
class Article(models.Model):
    name = models.CharField(max_length=100)

Artifact.link_to(Finding)


class ManyLinkableModelTest(TestCase):
    def setUp(self):
        self.article1 = Article.objects.create(name="article1")
        self.article2 = Article.objects.create(name="article2")
        self.finding1 = Finding.objects.create(name="finding1")

    def test_article_artifact(self):
        article_artifact = Artifact.objects.create(name="article artifact 1")
        article_artifact.relations.add(self.article1)
        self.assertEqual(article_artifact.relations.count(), 1)
        self.assertEqual(len(article_artifact.relations.all()), 1)

    def test_multi_artifact(self):
        article_artifact = Artifact.objects.create(name="article artifact 2")
        article_artifact.relations.add(self.article1)
        article_artifact.relations.add(self.finding1)
        self.assertEqual(article_artifact.relations.count(), 2)
        self.assertEqual(len(article_artifact.relations.all()), 2)
        self.assertEqual(len(article_artifact.relations.all(linked_type=Finding)), 1)
        self.assertEqual(len(article_artifact.relations.all(linked_type=[Article,])), 1)
        self.assertEqual(len(article_artifact.relations.all([Finding, Article])), 2)
        self.assertEqual(article_artifact.relations.all(linked_type=Finding)[0].name, self.finding1.name)

    def test_generic_artifact(self):
        artifact = Artifact.objects.create(name="generic artifact")
        artifact.relations.add(self.finding1)
        artifact.relations.add(self.article1)
        self.assertEqual(len(artifact.relations.all()), 2)
        self.assertEqual(len(artifact.relations.all(linked_type=Finding)), 1)
        self.assertEqual(len(artifact.relations.all(linked_type=[Article,])), 1)
        self.assertEqual(len(artifact.relations.all([Finding, Article])), 2)
        self.assertEqual(artifact.relations.all(linked_type=Finding)[0].name, self.finding1.name)

    def test_not_related(self):
        artifact = Artifact.objects.create(name="generic artifact 2")
        not_related = NotRelatedModel.objects.create(name="Not related")
        with self.assertRaises(artifact.LinkedModelDoesNotExist):
            artifact.relations.add(not_related)

    def test_remove(self):
        artifact = Artifact.objects.create(name="generic artifact 3")
        artifact.relations.add(self.article1)
        artifact.relations.add(self.article2)
        artifact.relations.add(self.finding1)
        self.assertEqual(len(artifact.relations.all()), 3)
        self.assertEqual(len(artifact.relations.all(linked_type=[Article, ])), 2)
        artifact.relations.remove(self.article2)
        self.assertEqual(len(artifact.relations.all(linked_type=[Article, ])), 1)
        artifact.relations.remove(self.article2)
        self.assertEqual(len(artifact.relations.all(linked_type=[Article, ])), 1)
        artifact.relations.remove(self.article1)
        self.assertEqual(len(artifact.relations.all(linked_type=[Article, ])), 0)

    def test_filter(self):
        artifact = Artifact.objects.create(name="generic artifact 4")
        artifact.relations.add(self.article1)
        artifact.relations.add(self.article2)
        artifact.relations.add(self.finding1)
        result = artifact.relations.filter(name="article1")
        self.assertEqual(len(result), 1)
        result = artifact.relations.filter(name__endswith="1")
        self.assertEqual(len(result), 2)

    def test_related_direct_access(self):
        artifact = Artifact.objects.create(name="generic artifact 5")
        artifact.relations.add(self.article1)
        artifact.relations.add(self.article2)
        findings_qs = artifact.findings.all()
        articles_qs = artifact.articles.all()
        self.assertEqual(findings_qs.count(), 0)
        self.assertEqual(articles_qs.count(), 2)

    def test_related_qs(self):
        artifact = Artifact.objects.create(name="generic artifact 6")
        artifact.relations.add(self.article1)
        artifact.relations.add(self.article2)
        findings_qs = artifact.findings.all()
        articles_qs = artifact.articles.all()
        self.assertEqual(findings_qs.count(), 0)
        self.assertEqual(articles_qs.count(), 2)

    def test_annotation(self):
        from django.db.models import Count
        artifact = Artifact.objects.create(name="generic artifact 6")
        artifact.relations.add(self.article1)
        artifact.relations.add(self.article2)
        artifacts = Artifact.objects.annotate(Count('articles')).all()
        self.assertEqual(artifacts[0].articles__count, 2)

    def test_create(self):
        artifact = Artifact.objects.create(name="generic artifact 6")
        artifact.relations.create(linked_type=Finding, name="Finding directly created")
        self.assertEqual(artifact.relations.count(), 1)
        self.assertEqual(artifact.findings.count(), 1)
        self.assertEqual(artifact.relations.all()[0].name, "Finding directly created")
        with self.assertRaises(AssertionError):
            artifact.relations.create(name="Finding directly created (should fail)")
        with self.assertRaises(artifact.LinkedModelDoesNotExist):
            artifact.relations.create(linked_type=NotRelatedModel, name="Misc model directly created (should fail)")


class OneLinkableModelTest(TestCase):
    def setUp(self):
        self.file_holder = FileHolder.objects.create(name="File Holder")

    def test_link(self):
        linked = OneLinked.objects.create(name="Linked", content_object=self.file_holder)
        self.assertEqual(self.file_holder.onelinked_set.count(), 1)
        self.assertEqual(linked.fileholder.name, "File Holder")
