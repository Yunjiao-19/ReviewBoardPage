from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.template.defaultfilters import timesince
from djblets.util.decorators import augment_method_from
from djblets.webapi.fields import (IntFieldType,
                                   ResourceFieldType,
                                   StringFieldType)

from reviewboard.reviews.models.commit_message_comment import CommitMessageComment
from reviewboard.webapi.base import WebAPIResource
from reviewboard.webapi.decorators import webapi_check_local_site
from reviewboard.webapi.resources import resources
from reviewboard.webapi.resources.base_comment import BaseCommentResource

class BaseReviewCommitMessageCommentResource(BaseCommentResource):
    """Base class for diff comment resources.

    Provides common fields and functionality for all commit message comment resources.
    """
    model = CommitMessageComment
    name = 'commit_message_comment'
    fields = BaseCommentResource.fields
    uri_object_key = 'comment_id'

    allowed_methods = ('GET',)

    def get_queryset(self, request, review_id=None, is_list=False,
                     *args, **kwargs):
        """Returns a queryset for Commit Message Comment models.

        This filters the query for comments on the specified review request
        which are either public or owned by the requesting user.

        """
        try:
            review_request = resources.review_request.get_object(
                request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise self.model.DoesNotExist

        q = self.model.objects.filter(
            commit__diffset__history__review_request=review_request,
            review__isnull=False)

        if is_list:
            if review_id:
                q = q.filter(review=review_id)

        order_by = kwargs.get('order-by', None)

        if order_by:
            q = q.order_by(*[
                field
                for field in order_by.split(',')
                if '__' not in field  # Don't allow joins
            ])

        return q

    def serialize_public_field(self, obj, **kwargs):
        return obj.review.get().public

    def serialize_timesince_field(self, obj, **kwargs):
        return timesince(obj.timestamp)

    def serialize_user_field(self, obj, **kwargs):
        return obj.review.get().user

    @webapi_check_local_site
    @augment_method_from(WebAPIResource)
    def get(self, *args, **kwargs):
        """Returns information on the comment."""
        pass
