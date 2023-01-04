"""
coding structure in the style of ./review_diff_comment.py
"""
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.utils import six
from djblets.util.decorators import augment_method_from
from djblets.webapi.decorators import (webapi_login_required,
                                       webapi_response_errors,
                                       webapi_request_fields)
from djblets.webapi.errors import (DOES_NOT_EXIST, INVALID_FORM_DATA,
                                   NOT_LOGGED_IN, PERMISSION_DENIED)
from djblets.webapi.fields import IntFieldType

from reviewboard.diffviewer.features import dvcs_feature
from reviewboard.diffviewer.models import DiffCommit
from reviewboard.webapi.decorators import webapi_check_local_site
from reviewboard.webapi.resources import resources
from reviewboard.webapi.resources.base_review_commit_comment import \
    BaseReviewCommitMessageCommentResource
from reviewboard.webapi.base import ImportExtraDataError
from reviewboard.reviews.models import CommitMessageComment, BaseComment

class ReviewCommitMessageCommentResource(BaseReviewCommitMessageCommentResource):
    """Provides information on comments made to commit messages in a review.
    
    If the review is a draft, then comments can be added, deleted, or
    changed on this list. However, if the review is already published,
    then no changes can be made.
    """
    allowed_methods = ('GET','POST','PUT','DELETE')
    policy_id = 'review_commit_comment'
    model_parent_key = 'review'

    mimetype_list_resource_name = 'review-commit-comments'
    mimetype_item_resource_name = 'review-commit-comment'
    
    def get_queryset(self, request, review_id, *args, **kwargs):
        q = super(ReviewCommitMessageCommentResource, self).get_queryset(
            request, *args, **kwargs)
        return q.filter(review=review_id)
    
    """
    The lines below CREATES a commit comment.
    """
    @webapi_check_local_site
    @webapi_login_required
    @webapi_response_errors(DOES_NOT_EXIST, INVALID_FORM_DATA,
                            NOT_LOGGED_IN, PERMISSION_DENIED)
    @webapi_request_fields(
        required=dict({
            'commit_id': {
                'type': IntFieldType,
                'description': 'The ID of the commit the comment is on.',
            },
        }, **BaseReviewCommitMessageCommentResource.REQUIRED_CREATE_FIELDS),
        optional=BaseReviewCommitMessageCommentResource.OPTIONAL_CREATE_FIELDS,
        allow_unknown=True,
    )
    def create(self, request, commit_id, *args, **kwargs):
        """Creates a new commit comment.

        This will create a new commit comment on this review. The review
        must be a draft review.

        Extra data can be stored later lookup. See
        :ref:`webapi2.0-extra-data` for more information.
        """

        try:
            review = resources.review.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return DOES_NOT_EXIST

        if not resources.review.has_modify_permissions(request, review):
            return self.get_no_access_error(request)

        comment_kwargs = {
            'issue_opened': bool(kwargs['issue_opened']),
            'rich_text': kwargs['text_type'] == self.TEXT_TYPE_MARKDOWN,
            'text': kwargs['text'].strip(),
            'commit_id': commit_id,
        }
        new_comment = CommitMessageComment(**comment_kwargs)
        try:
            self.import_extra_data(new_comment, new_comment.extra_data,
                                   kwargs['extra_fields'])
        except ImportExtraDataError as e:
            return e.error_payload

        if kwargs['issue_opened']:
            new_comment.issue_status = CommitMessageComment.OPEN
        else:
            new_comment.issue_status = None

        new_comment.save()
        review.commit_message_comments.add(new_comment)

        return 201, { self.item_result_key: new_comment, }

    """
    The lines below UPDATES a commit comment.
    """
    @webapi_check_local_site
    @webapi_login_required
    @webapi_response_errors(DOES_NOT_EXIST, NOT_LOGGED_IN, PERMISSION_DENIED)
    @webapi_request_fields(
        optional=BaseReviewCommitMessageCommentResource.OPTIONAL_UPDATE_FIELDS,
        allow_unknown=True,
    )
    def update(self, request, *args, **kwargs):
        """Updates a commit comment.

        This can update the text or line range of an existing comment.

        Extra data can be stored later lookup. See
        :ref:`webapi2.0-extra-data` for more information.
        """
        try:
            review = resources.review.get_object(request, *args, **kwargs)
            commitComment = self.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return DOES_NOT_EXIST

        if not resources.review.has_modify_permissions(request, review):
            return self.get_no_access_error(request)

        if not commitComment.issue_opened and kwargs.get('issue_opened', False):
            commitComment.issue_status = BaseComment.OPEN

        if commitComment.issue_opened and not kwargs.get('issue_opened', True):
            commitComment.issue_status = None

        self.set_text_fields(commitComment, 'text', **kwargs)
        commitComment.save()
        return 200, { self.item_result_key:commitComment }

    @webapi_check_local_site
    @augment_method_from(BaseReviewCommitMessageCommentResource)
    def delete(self, *args, **kwargs):
        """Deletes the comment.

        This will remove the comment from the review. This cannot be undone.

        Only comments on draft reviews can be deleted. Attempting to delete
        a published comment will return a Permission Denied error.

        Instead of a payload response, this will return :http:`204`.
        """
        pass

    @webapi_check_local_site
    @augment_method_from(BaseReviewCommitMessageCommentResource)
    def get_list(self, *args, **kwargs):
        """Returns the list of comments made on a commit.
        """
        pass


    def create_comment(self, request, comments_m2m, base_diff_commit_id, base_filediff_id=None,

                       **kwargs):
        """Create a review comment on a commit.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

            comments_m2m (django.db.models.ManyToManyField):
                The review's comments relation, where the new comment will be
                added.

            base_diff_commit_id (int, optional):
                The ID of the base commit for the :term:`cumulative diff` the
                comment is on.

            **kwargs (dict):
                Additional keyword arguments to pass on to the base class
                method.

        Returns:
            tuple or djblets.webapi.errors.WebAPIError:
            Either a successful payload containing the comment, or an error
            payload.
        """

        rsp = super(ReviewCommitMessageCommentResource, self).create_comment(
            comments_m2m=comments_m2m,
            save=False,
            **kwargs)

        if (isinstance(rsp, tuple) and
            isinstance(rsp[1], dict) and
            self.item_result_key in rsp[1]):
            comment = rsp[1][self.item_result_key]

            if (base_diff_commit_id is not None and
                dvcs_feature.is_enabled(request=request)):
                comment.base_diff_commit_id = base_diff_commit_id

            comment.save()
            comments_m2m.add(comment)

        return rsp

    def serialize_object(self, obj, request=None, *args, **kwargs):
        """Serialize a commit comment.

        Args:
            obj (reviewboard.reviews.models.diff_commit_comment.ReviewCommitMessageComment):
                The diff comment to serialize.

            request (django.http.HttpRequest, optional):
                The HTTP request from the client.

            *args (tuple):
                Additional positional arguments.

            **kwargs (dict):
                Additional keyword arguments.

        Returns:
            dict:
            The serialized commit comment.
        """
        result = super(ReviewCommitMessageCommentResource, self).serialize_object(
            obj, request=request, *args, **kwargs)


        return result

review_commit_comment_resource = ReviewCommitMessageCommentResource()
