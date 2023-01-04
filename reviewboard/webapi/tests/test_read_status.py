from __future__ import unicode_literals

import django
from django.contrib import auth
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.utils import six
from django.utils.timezone import get_current_timezone
from djblets.db.query import get_object_or_none
from djblets.features.testing import override_feature_check
from djblets.testing.decorators import add_fixtures
from djblets.webapi.errors import (DOES_NOT_EXIST,
                                   INVALID_FORM_DATA,
                                   PERMISSION_DENIED)
from djblets.webapi.testing.decorators import webapi_test_template
from kgb import SpyAgency
from pytz import timezone

from reviewboard.accounts.backends import AuthBackend
from reviewboard.accounts.models import LocalSiteProfile
from reviewboard.admin.server import build_server_url
from reviewboard.diffviewer.features import dvcs_feature
from reviewboard.reviews.models import (BaseComment, ReviewRequest,
                                        ReviewRequestDraft)
from reviewboard.reviews.signals import (review_request_closing,
                                         review_request_publishing,
                                         review_request_reopening)
from reviewboard.reviews.errors import CloseError, PublishError, ReopenError
from reviewboard.site.models import LocalSite
from reviewboard.webapi.errors import (CLOSE_ERROR, INVALID_REPOSITORY,
                                       PUBLISH_ERROR, REOPEN_ERROR,
                                       REPO_INFO_ERROR)
from reviewboard.webapi.resources import resources
from reviewboard.webapi.tests.base import BaseWebAPITestCase
from reviewboard.webapi.tests.mimetypes import (read_status_item_mimetype,
                                                read_status_list_mimetype,
                                                review_item_mimetype,
                                                review_request_item_mimetype,
                                                review_request_list_mimetype)
from reviewboard.webapi.tests.mixins import BasicTestsMetaclass
from reviewboard.webapi.tests.mixins_extra_data import (ExtraDataItemMixin,
                                                        ExtraDataListMixin)
from reviewboard.webapi.tests.urls import (get_repository_item_url,
                                           get_read_status_item_url,
                                           get_read_status_list_url,
                                           get_review_item_url,
                                           get_review_request_draft_url,
                                           get_review_request_item_url,
                                           get_review_request_list_url,
                                           get_user_item_url)

@six.add_metaclass(BasicTestsMetaclass)
class ResourceTests(SpyAgency, BaseWebAPITestCase):
    """Testing the Read Status API tests."""
    fixtures = ['test_users']
    sample_api_url = 'review-requests/<id>/read-status/'
    resource = resources.read_status

    def test_post(self):
        """Testing the POST review-requests/<id>/read-status/ API with custom
        read status
        """
        user1 = User.objects.create(username='doc1')
        user2 = User.objects.create(username='doc2')
        parent_review_request = self.create_review_request(publish=True)

        review_request = self.create_review_request(
            publish=True,
            commit_id='123',
            description_rich_text=True,
            depends_on=[parent_review_request],
            target_people=[user1, user2],
            extra_data={
                'key': {
                    'values': [1, 2, 3],
                },
                'boolean': True,
            })

        revision = review_request.get_latest_revision()
        file = '/example'
        self.client.force_login(user1)
        rsp = self.api_post(
            get_read_status_item_url(review_request),
            {
                'file': file,
                'revision': revision,
                'status': 1,
            },
            expected_mimetype = read_status_item_mimetype)

        self.assertEqual(rsp['stat'], 'ok')

    def test_get(self):
        """Testing the Read Status API tests."""
        self.create_read_status()
        rsp = self.api_get(get_read_status_list_url(),
                           expected_mimetype=read_status_list_mimetype)
        self.assertEqual(rsp['stat'], 'ok')