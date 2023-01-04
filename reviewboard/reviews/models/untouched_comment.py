from __future__ import unicode_literals

from django.db import models
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from reviewboard.diffviewer.models import FileDiff

from reviewboard.diffviewer.models import FileUntouchedComment

from reviewboard.reviews.models.base_comment import BaseComment

class UntouchedComment(BaseComment):
    """A comment on a review request that is not tied to any code or file.

    A general comment on a review request is used when a comment is not tied
    to specific lines of code or a special file attachment, and an issue is
    opened. Examples include suggestions for testing or pointing out errors
    in the change description.
    """
    anchor_prefix = 'ucomment'
    comment_type = 'untouched'
    untouchedfile = models.ForeignKey(FileUntouchedComment, verbose_name=_('file untouchedcomment'),
                                  related_name="file_untouchedcomment")
    first_line = models.PositiveIntegerField(_("first line"), blank=True,
                                             null=True)
    num_lines = models.PositiveIntegerField(_("number of lines"), blank=True,
                                            null=True)

    last_line = property(lambda self: self.first_line + self.num_lines - 1)

    def get_absolute_url(self):
        return "%sdiff/" % (
            self.get_review_request().get_absolute_url())

    class Meta(BaseComment.Meta):
        db_table = 'reviews_untouched_comment'
        verbose_name = _('Untouched Comment')
        verbose_name_plural = _('Untouched Comments')