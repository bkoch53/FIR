from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase

from findings import models


# Create your tests here.


class BusinessLineTestCase(TestCase):
    def setUp(self):
        self.root_1 = models.BusinessLine.add_root(name='Root 1')
        self.child11 = self.root_1.add_child(name='Child 11')
        self.child12 = self.root_1.add_child(name='Child 12')

        self.root_2 = models.BusinessLine.add_root(name='Root 2')
        self.child21 = self.root_2.add_child(name='Child 21')
        self.child22 = self.root_2.add_child(name='Child 22')

        self.admin = User.objects.create_user('admin', 'admin@example.com', 'admin')
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'password')
        self.user3 = User.objects.create_user('user3', 'user3@example.com', 'password')
        self.user4 = User.objects.create_user('user4', 'user4@example.com', 'password')
        self.user5 = User.objects.create_user('user5', 'user5@example.com', 'password')

        adder, created = Group.objects.get_or_create(name='Adder')
        changer, created = Group.objects.get_or_create(name='Changer')
        deleter, created = Group.objects.get_or_create(name='Deleter')

        self.user5.groups.add(changer)

        add = Permission.objects.get(codename='add_finding')
        change = Permission.objects.get(codename='change_finding')
        delete = Permission.objects.get(codename='delete_finding')

        adder.permissions.clear()
        adder.permissions.add(add)

        changer.permissions.clear()
        changer.permissions.add(change, delete)

        deleter.permissions.clear()
        deleter.permissions.add(delete)

        models.AccessControlEntry.objects.create(user=self.user1, business_line=self.root_1, role=adder)

    def test_superuser(self):
        for perm in ['findings.change_finding', 'findings.delete_finding', 'findings.add_finding']:
            self.assertTrue(self.admin.has_perm(perm, obj=self.root_1))
            self.assertTrue(self.admin.has_perm(perm, obj=self.child11))
            self.assertTrue(self.admin.has_perm(perm, obj=self.child22))

    def test_direct_permission(self):
        self.assertTrue(self.user5.has_perm('findings.change_finding', obj=self.root_1))
        self.assertTrue(self.user5.has_perm('findings.delete_finding', obj=self.child22))
        self.assertFalse(self.user5.has_perm('findings.add_finding', obj=self.root_2))

    def test_tree_permission(self):
        self.assertTrue(self.user1.has_perm('findings.add_finding', obj=self.root_1))
        self.assertTrue(self.user1.has_perm('findings.add_finding', obj=self.child11))
        self.assertFalse(self.user1.has_perm('findings.add_finding', obj=self.root_2))

    def test_on_model_class(self):
        self.assertTrue(self.user1.has_perm('findings.add_finding', obj=models.BusinessLine))
        self.assertTrue(self.user1.has_perm('findings.add_finding', obj=models.BusinessLine))
        self.assertFalse(self.user1.has_perm('findings.delete_finding', obj=models.BusinessLine))
        self.assertTrue(self.user5.has_perm('findings.change_finding', obj=models.BusinessLine))
        self.assertFalse(self.user5.has_perm('findings.add_finding', obj=models.BusinessLine))
        self.assertTrue(self.admin.has_perm('findings.add_finding', obj=models.BusinessLine))


class FindingTestCase(TestCase):
    fixtures = ['findings/fixtures/seed_data.json', ]

    def setUp(self):
        self.root_1 = models.BusinessLine.add_root(name='Root 1')
        self.child11 = self.root_1.add_child(name='Child 11')
        self.child12 = self.root_1.add_child(name='Child 12')

        self.root_2 = models.BusinessLine.add_root(name='Root 2')
        self.child21 = self.root_2.add_child(name='Child 21')
        self.child22 = self.root_2.add_child(name='Child 22')

        self.admin = User.objects.create_user('admin', 'admin@example.com', 'admin')
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'password')
        self.user3 = User.objects.create_user('user3', 'user3@example.com', 'password')
        self.user4 = User.objects.create_user('user4', 'user4@example.com', 'password')
        self.user5 = User.objects.create_user('user5', 'user5@example.com', 'password')

        adder, created = Group.objects.get_or_create(name='Adder')
        changer, created = Group.objects.get_or_create(name='Changer')
        deleter, created = Group.objects.get_or_create(name='Deleter')

        self.user5.groups.add(changer)

        add = Permission.objects.get(codename='add_finding')
        change = Permission.objects.get(codename='change_finding')
        delete = Permission.objects.get(codename='delete_finding')

        adder.permissions.clear()
        adder.permissions.add(add)

        changer.permissions.clear()
        changer.permissions.add(change, delete)

        deleter.permissions.clear()
        deleter.permissions.add(delete)

        models.AccessControlEntry.objects.create(user=self.user1, business_line=self.root_1, role=adder)

        bale, created = models.BaleCategory.objects.get_or_create(name="Bale category", category_number=1)
        detections, created = models.LabelGroup.objects.get_or_create(name='detection')
        detection, created = models.Label.objects.get_or_create(name='detection 1', group=detections)
        category, created = models.FindingCategory.objects.get_or_create(name="Finding category",
                                                                          bale_subcategory=bale)
        self.finding_root_1, created = models.Finding.objects.get_or_create(subject="Finding Root 1",
                                                                              description="Test Finding",
                                                                              opened_by=self.user3, category=category,
                                                                              detection=detection, severity=1)
        self.finding_child_12, created = models.Finding.objects.get_or_create(subject="Finding Child 12",
                                                                                description="Test Finding",
                                                                                opened_by=self.admin, category=category,
                                                                                detection=detection, severity=1)
        self.finding_child_22, created = models.Finding.objects.get_or_create(subject="Finding Child 22",
                                                                                description="Test Finding",
                                                                                opened_by=self.admin, category=category,
                                                                                detection=detection, severity=1)
        if created:
            self.finding_root_1.concerned_business_lines = [self.root_1, ]
            self.finding_root_1.main_business_lines = [self.root_1, ]
            self.finding_root_1.save()
            self.finding_child_12.concerned_business_lines = [self.child12, ]
            self.finding_child_12.main_business_lines = [self.root_1, ]
            self.finding_child_12.save()
            self.finding_child_22.concerned_business_lines = [self.child22, ]
            self.finding_child_22.main_business_lines = [self.root_2, ]
            self.finding_child_22.save()

    def test_superuser(self):
        for perm in ['findings.change_finding', 'findings.delete_finding', 'findings.add_finding']:
            self.assertTrue(self.admin.has_perm(perm, obj=self.finding_root_1))
            self.assertTrue(self.admin.has_perm(perm, obj=self.finding_child_12))
            self.assertTrue(self.admin.has_perm(perm, obj=self.finding_child_22))

    def test_direct_permission(self):
        self.assertTrue(self.user5.has_perm('findings.change_finding', obj=self.finding_root_1))
        self.assertFalse(self.user5.has_perm('findings.add_finding', obj=self.finding_root_1))
        self.assertTrue(self.user5.has_perm('findings.change_finding', obj=self.finding_child_12))
        self.assertFalse(self.user5.has_perm('findings.add_finding', obj=self.finding_child_12))
        self.assertTrue(self.user5.has_perm('findings.change_finding', obj=self.finding_child_22))
        self.assertFalse(self.user5.has_perm('findings.add_finding', obj=self.finding_child_22))

    def test_tree_permission(self):
        self.assertTrue(self.user1.has_perm('findings.add_finding', obj=self.finding_root_1))
        self.assertFalse(self.user1.has_perm('findings.delete_finding', obj=self.finding_root_1))
        self.assertTrue(self.user1.has_perm('findings.add_finding', obj=self.finding_child_12))
        self.assertFalse(self.user1.has_perm('findings.delete_finding', obj=self.finding_child_12))
        self.assertFalse(self.user1.has_perm('findings.add_finding', obj=self.finding_child_22))
        self.assertFalse(self.user1.has_perm('findings.delete_finding', obj=self.finding_child_22))

    def test_on_model_class(self):
        self.assertTrue(self.user1.has_perm('findings.add_finding', obj=models.Finding))
        self.assertFalse(self.user1.has_perm('findings.delete_finding', obj=models.Finding))
        self.assertTrue(self.user5.has_perm('findings.change_finding', obj=models.Finding))
        self.assertTrue(self.admin.has_perm('findings.change_finding', obj=models.Finding))
        self.assertFalse(self.user4.has_perm('findings.change_finding', obj=models.Finding))

    def test_creator(self):
        self.assertTrue(self.user3.has_perm('findings.view_findings', obj=self.finding_root_1))
        self.assertFalse(self.user3.has_perm('findings.delete_finding', obj=self.finding_root_1))


class QuerySetBLTestCase(TestCase):
    def setUp(self):
        self.root_1 = models.BusinessLine.add_root(name='Root 1')
        self.child11 = self.root_1.add_child(name='Child 11')
        self.child12 = self.root_1.add_child(name='Child 12')

        self.root_2 = models.BusinessLine.add_root(name='Root 2')
        self.child21 = self.root_2.add_child(name='Child 21')
        self.child22 = self.root_2.add_child(name='Child 22')

        self.admin = User.objects.create_user('admin', 'admin@example.com', 'admin')
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'password')
        self.user3 = User.objects.create_user('user3', 'user3@example.com', 'password')
        self.user4 = User.objects.create_user('user4', 'user4@example.com', 'password')
        self.user5 = User.objects.create_user('user5', 'user5@example.com', 'password')

        adder, created = Group.objects.get_or_create(name='Adder')
        changer, created = Group.objects.get_or_create(name='Changer')
        deleter, created = Group.objects.get_or_create(name='Deleter')

        self.user5.groups.add(changer)

        add = Permission.objects.get(codename='add_finding')
        change = Permission.objects.get(codename='change_finding')
        delete = Permission.objects.get(codename='delete_finding')

        adder.permissions.clear()
        adder.permissions.add(add)

        changer.permissions.clear()
        changer.permissions.add(change, delete)

        deleter.permissions.clear()
        deleter.permissions.add(delete)

        models.AccessControlEntry.objects.create(user=self.user1, business_line=self.root_1, role=adder)
        models.AccessControlEntry.objects.create(user=self.user2, business_line=self.child11, role=adder)
        models.AccessControlEntry.objects.create(user=self.user2, business_line=self.root_2, role=deleter)

    def test_superuser(self):
        for perm in ['findings.change_finding', 'findings.delete_finding', 'findings.add_finding']:
            self.assertEqual(models.BusinessLine.authorization.for_user(self.admin, permission=perm).count(), 6)

    def test_direct_permission(self):
        self.assertEqual(
            models.BusinessLine.authorization.for_user(self.user5, permission='findings.change_finding').count(), 6)
        self.assertEqual(
            models.BusinessLine.authorization.for_user(self.user5, permission='findings.add_finding').count(), 0)

    def test_tree_permission(self):
        self.assertEqual(
            models.BusinessLine.authorization.for_user(self.user1, permission='findings.add_finding').count(), 3)
        self.assertEqual(
            models.BusinessLine.authorization.for_user(self.user1, permission='findings.delete_finding').count(), 0)

    def test_no_permission(self):
        self.assertEqual(models.BusinessLine.authorization.for_user(self.admin).count(), 6)
        self.assertEqual(models.BusinessLine.authorization.for_user(self.user1).count(), 3)
        self.assertEqual(models.BusinessLine.authorization.for_user(self.user2).count(), 4)
