from __future__ import unicode_literals

from django.contrib.auth.models import User
from djblets.testing.decorators import add_fixtures

from reviewboard.diffviewer.models import RawFileDiffData
from reviewboard.reviews.models import ReadStatus
from reviewboard.scmtools.errors import ChangeNumberInUseError
from reviewboard.site.models import LocalSite
from reviewboard.testing import TestCase


class ReadStatusManagerTests(TestCase):
    """Unit tests for reviewboard.reviews.managers.ReviewRequestManager."""

    fixtures = ['test_users']
    # This manager is not being used, ignore
    # def test_get_or_create_from_data(self):
    #     """Testing ReviewRequest.objects.create with LocalSite"""
    #     data = {'user_id' : 1,
    #     'review_request_id' : 2,
    #     'revision_id' : 1,
    #     'file_name' : 'covid-positive',
    #     'status' : 0,
    #     'timestamp' : 0}
    #     raw_file_diff_data = ReadStatus.objects.get_or_create(data)