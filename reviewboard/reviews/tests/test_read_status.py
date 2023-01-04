from __future__ import unicode_literals

import kgb
from django.contrib.auth.models import User
from djblets.testing.decorators import add_fixtures

from reviewboard.reviews.models import ReadStatus
from reviewboard.testing import TestCase

class ReadStatusTests(kgb.SpyAgency, TestCase):
    """Tests for reviewboard.reviews.models.ReadStatus."""
    fixtures = ['test_users', 'test_scmtools']


    def test_can_get_read_status(self):
        user1 = User.objects.create(username = 'doc1')
        parent_review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(
            create_repository=True,
            publish=True,
            commit_id='123',
            depends_on=[parent_review_request],
            target_people=[user1],
            extra_data={
                'key': {
                    'values': [1, 2, 3],
                },
                'boolean': True,
            })

        revision = self.create_diffset(review_request)
        file_name = '/example'
        ReadStatus.objects.create(user=user1, review_request=review_request,
                                  revision=revision, file_name=file_name, status=0)
        self.assertEqual(ReadStatus.get_read_status(user1, file_name, review_request, revision), 0)
        self.assertEqual(ReadStatus.get_read_status(user1, '/lost', review_request, revision), None)

    def test_can_get_read_status_by_default(self):
        user1 = User.objects.create(username = 'doc1')
        parent_review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(
            create_repository=True,
            publish=True,
            commit_id='123',
            depends_on=[parent_review_request],
            target_people=[user1],
            extra_data={
                'key': {
                    'values': [1, 2, 3],
                },
                'boolean': True,
            })

        revision = self.create_diffset(review_request)
        file_name = '/example'
        ReadStatus.objects.create(user=user1, review_request=review_request,
                                  revision=revision, file_name=file_name)
        self.assertEqual(ReadStatus.get_read_status(user1, file_name, review_request, revision), 0)
        self.assertEqual(ReadStatus.get_read_status(user1, '/lost', review_request, revision), None)

    def test_can_get_read_status_with_collective_ownership(self):
        user1 = User.objects.create(username = 'doc1')
        user2 = User.objects.create(username = 'doc2')
        user3 = User.objects.create(username = 'doc3')
        parent_review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(
            create_repository=True,
            publish=True,
            commit_id='123',
            depends_on=[parent_review_request],
            target_people=[user1,user2],
            extra_data={
                'key': {
                    'values': [1, 2, 3],
                },
                'boolean': True,
            })


        revision = self.create_diffset(review_request)     
        file_name = '/example'
        ReadStatus.objects.create(user=user1, review_request=review_request,
                                  revision=revision, file_name=file_name, status=0, timestamp='2022-03-01 11:45')
        ReadStatus.objects.create(user=user2, review_request=review_request,
                                  revision=revision, file_name=file_name, status=1, timestamp='2022-03-01 11:42')
        ReadStatus.objects.create(user=user3, review_request=review_request,
                                  revision=revision, file_name=file_name, status=2, timestamp='2022-03-02 13:45')
        self.assertEqual(ReadStatus.get_read_status(user1, file_name, review_request, revision), 0)
        self.assertEqual(ReadStatus.get_read_status(user2, file_name, review_request, revision), 1)
        self.assertEqual(ReadStatus.get_read_status(user3, file_name, review_request, revision), 2)
        self.assertEqual(ReadStatus.get_read_status(user1, '/lost', review_request, revision), None)

    def test_can_get_file_name(self):
        user1 = User.objects.create(username = 'doc1')
        parent_review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(
            create_repository=True,
            publish=True,
            commit_id='123',
            depends_on=[parent_review_request],
            target_people=[user1],
            extra_data={
                'key': {
                    'values': [1, 2, 3],
                },
                'boolean': True,
            })

        revision = self.create_diffset(review_request)
        file_name = '/example'
        read_status = 0
        ReadStatus.objects.create(user=user1, review_request=review_request,
                                  revision=revision, file_name=file_name, status=read_status, timestamp='2022-03-01 11:45')
        self.assertEqual(ReadStatus.get_file_name(user1, review_request, revision, read_status), '/example')
        self.assertEqual(ReadStatus.get_file_name(user1, review_request, revision, 1), None)

    def test_can_get_revision(self):
        user1 = User.objects.create(username = 'doc1')
        parent_review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(
            create_repository=True,
            publish=True,
            commit_id='123',
            depends_on=[parent_review_request],
            target_people=[user1],
            extra_data={
                'key': {
                    'values': [1, 2, 3],
                },
                'boolean': True,
            })

        revision = self.create_diffset(review_request)
        file_name = '/example'
        read_status = 0
        ReadStatus.objects.create(user=user1, review_request=review_request,
                                  revision=revision, file_name=file_name, status=read_status, timestamp='2022-03-01 11:45')
        self.assertEqual(ReadStatus.get_revision(user1, file_name, review_request, read_status), revision)
        self.assertEqual(ReadStatus.get_revision(user1, '/lost', review_request, read_status), None)

    def test_can_get_review_request(self):
        user1 = User.objects.create(username = 'doc1')
        parent_review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(
            create_repository=True,
            publish=True,
            commit_id='123',
            depends_on=[parent_review_request],
            target_people=[user1],
            extra_data={
                'key': {
                    'values': [1, 2, 3],
                },
                'boolean': True,
            })

        revision = self.create_diffset(review_request)
        file_name = '/example'
        read_status = 0
        ReadStatus.objects.create(user=user1, review_request=review_request,
                                  revision=revision, file_name=file_name, status=read_status, timestamp='2022-03-01 11:45')
        self.assertEqual(ReadStatus.get_review_request(user1, file_name, revision, read_status), review_request)
        self.assertEqual(ReadStatus.get_review_request(user1, '/lost', revision, read_status), None)

    def test_can_get_user(self):
        user1 = User.objects.create(username = 'doc1')
        parent_review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(
            create_repository=True,
            publish=True,
            commit_id='123',
            depends_on=[parent_review_request],
            target_people=[user1],
            extra_data={
                'key': {
                    'values': [1, 2, 3],
                },
                'boolean': True,
            })

        revision = self.create_diffset(review_request)
        file_name = '/example'
        read_status = 0
        ReadStatus.objects.create(user=user1, review_request=review_request,
                                  revision=revision, file_name=file_name, status=read_status, timestamp='2022-03-01 11:45')
        self.assertEqual(ReadStatus.get_user(file_name, review_request, revision, read_status), user1)    
        self.assertEqual(ReadStatus.get_user('/lost', review_request, revision, read_status), None) 

    def test_can_get_extra_data(self):
        user1 = User.objects.create(username = 'doc1')
        parent_review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(
            create_repository=True,
            publish=True,
            commit_id='123',
            depends_on=[parent_review_request],
            target_people=[user1],
            extra_data={
                'key': {
                    'values': [1, 2, 3],
                },
                'boolean': True,
            })

        revision = self.create_diffset(review_request)
        file_name = '/example'
        read_status = 0
        ReadStatus.objects.create(user=user1, review_request=review_request,
                                  revision=revision, file_name=file_name, status=read_status, timestamp='2022-03-01 11:45')
        self.assertEqual(ReadStatus.get_extra_data(user1, file_name, review_request, revision, read_status), {})  
        self.assertEqual(ReadStatus.get_extra_data(user1, '/lost', review_request, revision, read_status), None)

    def test_can_create_read_status(self):
        user1 = User.objects.create(username = 'doc1')
        user2 = User.objects.create(username = 'doc2')
        parent_review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(
            create_repository=True,
            publish=True,
            commit_id='123',
            depends_on=[parent_review_request],
            target_people=[user1,user2],
            extra_data={
                'key': {
                    'values': [1, 2, 3],
                },
                'boolean': True,
            })

        revision = self.create_diffset(review_request)
        file_name = '/example'
        object = ReadStatus.objects.create(user=user1, review_request=review_request,
                                  revision=revision, file_name=file_name, status=0)

        self.assertEqual(object.user, user1)
        self.assertEqual(object.review_request, review_request)
        self.assertEqual(object.revision, revision)
        self.assertEqual(object.file_name, file_name)
        self.assertEqual(object.extra_data, {})