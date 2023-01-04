
from django.db import models
from django.utils.translation import ugettext_lazy as _

from reviewboard.reviews.models.base_comment import BaseComment
from reviewboard.diffviewer.models.diffcommit import DiffCommit

class CommitMessageComment(BaseComment):
    """A comment on a commit message."""
    anchor_prefix = "cmcomment"
    comment_type = "commit"
    commit = models.ForeignKey(DiffCommit, verbose_name=_('commit'),
                                   related_name="comments")

    class Meta(BaseComment.Meta):
        db_table = 'reviews_commitmessagecomment'
        verbose_name = _('Commit Message Comment')
        verbose_name_plural = _('Commit Message Comments')