from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from djblets.util.decorators import augment_method_from
from djblets.webapi.decorators import (webapi_login_required,
                                       webapi_response_errors,
                                       webapi_request_fields)
from djblets.webapi.errors import (DOES_NOT_EXIST, INVALID_FORM_DATA,
                                   NOT_LOGGED_IN, PERMISSION_DENIED)

from djblets.webapi.fields import IntFieldType, StringFieldType

from reviewboard.diffviewer.models import FileUntouchedComment
from reviewboard.reviews.models import UntouchedComment
from reviewboard.reviews.models import Review

from reviewboard.webapi.decorators import webapi_check_local_site
from reviewboard.webapi.resources import resources
from reviewboard.webapi.resources.base_untouched_comment import \
    BaseUntouchedCommentResource


class ReviewUntouchedCommentResource(BaseUntouchedCommentResource):
    """Provides information on diff comments made on a review.

    If the review is a draft, then comments can be added, deleted, or
    changed on this list. However, if the review is already published,
    then no changes can be made.
    """
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    policy_id = 'review_untouched_comment'
    model_parent_key = 'review'

    mimetype_list_resource_name = 'review-untouched-comments'
    mimetype_item_resource_name = 'review-untouched-comment'

    def get_queryset(self, request, review_id, *args, **kwargs):
        q = super(ReviewUntouchedCommentResource, self).get_queryset(
            request, *args, **kwargs)
        return q.filter(review=review_id)

    @webapi_check_local_site
    @webapi_login_required
    @webapi_response_errors(DOES_NOT_EXIST, INVALID_FORM_DATA,
                            NOT_LOGGED_IN, PERMISSION_DENIED)
    @webapi_request_fields(
        required=dict({
            'first_line': {
                'type': IntFieldType,
                'description': 'The line number the comment starts at.',
            },
            'num_lines': {
                'type': IntFieldType,
                'description': 'The number of lines the comment spans.',
            },
            'file_path': {
                'type': StringFieldType,
                'description': 'The ID of the file diff the comment is on.',
            },
            'source_file_hashcode': {
                'type': StringFieldType,
                'description': 'The ID of the file diff the comment is on.',
            },

        }, **BaseUntouchedCommentResource.REQUIRED_CREATE_FIELDS),
        allow_unknown=True,
    )
    
    def create(self, request, *args, **kwargs):
        """Creates a new diff comment.

        This will create a new diff comment on this review. The review
        must be a draft review.

        Extra data can be stored later lookup. See
        :ref:`webapi2.0-extra-data` for more information.
        """

        file_untouched_comment = FileUntouchedComment.objects.filter(untouched_file_path=kwargs['file_path'],untouched_file_hashcode=kwargs['source_file_hashcode'])
        if not file_untouched_comment:
            file_untouched_comment = FileUntouchedComment()
            file_untouched_comment.untouched_file_path=kwargs['file_path']
            file_untouched_comment.untouched_file_hashcode=kwargs['source_file_hashcode']
            file_untouched_comment.save()
        else:
            file_untouched_comment=file_untouched_comment[0]
        
        try:
            review = resources.review.get_object(request, *args, **kwargs)

        except ObjectDoesNotExist:
            return DOES_NOT_EXIST

        if not resources.review.has_modify_permissions(request, review):
            return self.get_no_access_error(request)

        return self.create_comment(fields=('first_line', 'num_lines'),
                            file_untouched_comment=file_untouched_comment,
                            review=review,
                            request=request,
                            comments_m2m=review.untouched_comments,
                            **kwargs)

    @webapi_check_local_site
    @webapi_login_required
    @webapi_response_errors(DOES_NOT_EXIST, NOT_LOGGED_IN, PERMISSION_DENIED)
    @webapi_request_fields(
        optional=dict({
            'first_line': {
                'type': IntFieldType,
                'description': 'The line number the comment starts at.',
            },
            'num_lines': {
                'type': IntFieldType,
                'description': 'The number of lines the comment spans.',
            },
        }, **BaseUntouchedCommentResource.OPTIONAL_UPDATE_FIELDS),
        allow_unknown=True,
    )
    def update(self, request, *args, **kwargs):
        """Updates a diff comment.

        This can update the text or line range of an existing comment.

        Extra data can be stored later lookup. See
        :ref:`webapi2.0-extra-data` for more information.
        """
        try:
            resources.review_request.get_object(request, *args, **kwargs)
            review = resources.review.get_object(request, *args, **kwargs)
            untouched_comment = self.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return DOES_NOT_EXIST

        return self.update_comment(request=request,
                                   review=review,
                                   comment=untouched_comment,
                                   update_fields=('first_line', 'num_lines'),
                                   **kwargs)

    @webapi_check_local_site
    @augment_method_from(BaseUntouchedCommentResource)
    def delete(self, *args, **kwargs):
        """Deletes the comment.

        This will remove the comment from the review. This cannot be undone.

        Only comments on draft reviews can be deleted. Attempting to delete
        a published comment will return a Permission Denied error.

        Instead of a payload response, this will return :http:`204`.
        """
        pass

    @webapi_check_local_site
    @augment_method_from(BaseUntouchedCommentResource)
    def get_list(self, *args, **kwargs):
        """Returns the list of comments made on a review.

        This list can be filtered down by using the ``?line=`` and
        ``?interdiff-revision=``.

        To filter for comments that start on a particular line in the file,
        using ``?line=``.

        To filter for comments that span revisions of diffs, you can specify
        the second revision in the range using ``?interdiff-revision=``.
        """
        pass

    def create_comment(self, file_untouched_comment, request, comments_m2m, **kwargs):
        """Create a review comment.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

            comments_m2m (django.db.models.ManyToManyField):
                The review's comments relation, where the new comment will be
                added.

            base_filediff_id (int, optional):
                The ID of the base filediff for the :term:`cumulative diff` the
                comment is on.

            **kwargs (dict):
                Additional keyword arguments to pass on to the base class
                method.

        Returns:
            tuple or djblets.webapi.errors.WebAPIError:
            Either a successful payload containing the comment, or an error
            payload.
        """
        rsp = super(ReviewUntouchedCommentResource, self).create_comment(
            comments_m2m=comments_m2m,
            save=False,
            **kwargs)

        if (isinstance(rsp, tuple) and
            isinstance(rsp[1], dict) and
            self.item_result_key in rsp[1]):
            comment = rsp[1][self.item_result_key]

            comment.untouchedfile=file_untouched_comment
            comment.save()
            comments_m2m.add(comment)

        return rsp

review_untouched_comment_resource = ReviewUntouchedCommentResource()
