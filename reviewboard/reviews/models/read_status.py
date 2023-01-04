from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from reviewboard.reviews.models.review_request import ReviewRequest
from reviewboard.diffviewer.models.diffset import DiffSet
from django.utils import timezone
from djblets.db.fields import JSONField
from reviewboard.reviews.managers import ReadStatusManager
from reviewboard.reviews.models.group import Group
import datetime

@python_2_unicode_compatible
class ReadStatus(models.Model):
    """ A representation of the read status for a single file diff

    """
    #: The date format that this model uses.
    ISO_DATE_FORMAT = '%Y-%m-%d %H:%M:%S%z'

    user = models.ForeignKey(User, verbose_name=_("user id"),
                             related_name="read")

    review_request = models.ForeignKey(ReviewRequest,
                                       related_name="read",
                                       verbose_name=_("review request id"))

    revision = models.ForeignKey(DiffSet, related_name='read',
                                 verbose_name="revision id")

    file_name = models.CharField(
        _('file name'), max_length=1024)

    status = models.IntegerField(_('read status'),default = 0)
    # 0: unread; 1: tentatively read; 2: read

    def return_now():
        return timezone.now()-timezone.timedelta(hours=4)

    timestamp = models.DateTimeField(('timestamp'), default=return_now)

    extra_data = JSONField(null=True)

    objects = ReadStatusManager()

    @staticmethod
    def get_read_status(user, file_name, review_request, revision):
        """Returns the user's read status of the file from a specific revision 
        from review request.    

        Args:
            user(django.contrib.auth.models.User): 
                The user that is requesting for read status.
            
            file_name(string):
                The file's name whose read status is being queried.

            review_request(reviewboard.reviews.models.ReviewRequest):
                The review request for this query.
            
            revision(reviewboard.diffviewer.models.Revision):
                The revision version of the review request.

        Returns:
            read_status(reviewboard.reviews.models.ReadStatus):
                The read status of this query. None is returned upon invalid
                status, or a failed type check of the arguments.
        """
        try:
            read_status = ReadStatus.objects.filter(user=user, file_name=file_name, 
            review_request=review_request, revision=revision).latest()
            return read_status.status
        except (ReadStatus.DoesNotExist, TypeError) as e:
            return None

    @staticmethod
    def get_file_name(user, review_request, revision, read_status):
        """Returns the file name of the file from a specific revision from review
        request that has a specific read status.    

        Args:
            user(django.contrib.auth.models.User): 
                The user that is requesting for read status.
            
            read_status(reviewboard.reviews.models.ReadStatus):
                The read status of this query. 

            review_request(reviewboard.reviews.models.ReviewRequest):
                The review request for this query.
            
            revision(reviewboard.diffviewer.models.Revision):
                The revision version of the review request.

        Returns:
            file_name(string):
                The file's name of this query. None is returned upon invalid
                status, or a failed type check of the arguments.
        """
        try:
            read_status = ReadStatus.objects.filter(user=user, review_request=review_request,
            revision=revision, status=read_status).latest()
            return read_status.file_name
        except (ReadStatus.DoesNotExist, TypeError) as e:
            return None

    @staticmethod
    def get_revision(user, file_name, review_request, read_status):
        """Returns the user's revision version of the file from the review request that has
        the current read status.   

        Args:
            user(django.contrib.auth.models.User): 
                The user that is requesting for read status.
            
            file_name(string):
                The file's name whose revision version is being queried.

            review_request(reviewboard.reviews.models.ReviewRequest):
                The review request for this query
            
            read_status(reviewboard.reviews.models.ReadStatus):
                The read status of this query. 

        Returns:
            revision(reviewboard.diffviewer.models.Revision):
                The revision version of the review request. None is returned upon invalid
                status, or a failed type check of the arguments.
        """
        try:
            read_status = ReadStatus.objects.filter(user=user, file_name=file_name,
            review_request=review_request, status=read_status).latest()
            return read_status.revision
        except (ReadStatus.DoesNotExist, TypeError) as e:
            return None

    @staticmethod
    def get_review_request(user, file_name, revision, read_status):
        """Returns the user's review request of the file with a specific revision 
        version and has the current read status.    

        Args:
            user(django.contrib.auth.models.User): 
                The user that is requesting for read status.
            
            file_name(string):
                The file's name whose review request is being queried.

            revision(reviewboard.diffviewer.models.Revision):
                The revision version of the review request.

            read_status(reviewboard.reviews.models.ReadStatus):
                The read status of this query. 

        Returns:
            review_request(reviewboard.reviews.models.ReviewRequest):
                The review request for this query. None is returned upon invalid
                status, or a failed type check of the arguments.
        """
        try:
            read_status = ReadStatus.objects.filter(user=user, file_name=file_name,
            revision=revision, status=read_status).latest()
            return read_status.review_request
        except (ReadStatus.DoesNotExist, TypeError) as e:
            return None

    @staticmethod
    def get_user(file_name, review_request, revision, read_status):
        """Returns the user whose review request of the file with a specific revision 
        version has the current read status.    

        Args:
            file_name(string):
                The file's name whose user is being queried.

            review_request(reviewboard.reviews.models.ReviewRequest):
                The review request for this query.

            revision(reviewboard.diffviewer.models.Revision):
                The revision version of the review request.

            read_status(reviewboard.reviews.models.ReadStatus):
                The read status of this query. 

        Returns:
            user(django.contrib.auth.models.User): 
                The user that is being queried. None is returned upon invalid
                status, or a failed type check of the arguments.
        """
        try:
            read_status = ReadStatus.objects.filter(file_name=file_name, review_request=review_request,
            revision=revision, status=read_status).latest()
            return read_status.user
        except (ReadStatus.DoesNotExist, TypeError) as e:
            return None

    @staticmethod
    def get_extra_data(user, file_name, review_request, revision, read_status):
        """Returns the data stored in the user's review request of the file with a 
        specific revision version that has the current read status.    

        Args:
            user(django.contrib.auth.models.User): 
                The user in this query.
            
            file_name(string):
                The file's name whose extra data is being queried.

            review_request(reviewboard.reviews.models.ReviewRequest):
                The review request for this query.

            revision(reviewboard.diffviewer.models.Revision):
                The revision version of the review request.

            read_status(reviewboard.reviews.models.ReadStatus):
                The read status of this query. 

        Returns:
            extra_data(Any):
                Data stored inside this read status. None is returned upon invalid
                status, or a failed type check of the arguments.
        """
        try:
            read_status = ReadStatus.objects.filter(user=user, file_name=file_name, review_request=review_request,
            revision=revision, status=read_status).latest()
            return read_status.extra_data
        except (ReadStatus.DoesNotExist, TypeError) as e:
            return None

    def __str__():
        pass

    class Meta:
        app_label = 'reviews'
        db_table = 'reviews_readstatus'
        verbose_name = _('Read Status')
        verbose_name_plural = _('Read Status')
        get_latest_by = 'timestamp'