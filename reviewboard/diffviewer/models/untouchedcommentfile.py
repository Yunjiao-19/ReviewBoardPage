
from django.db import models
# from reviewboard.reviews.models import ReviewRequest
# from django.utils.translation import ugettext_lazy as _

class FileUntouchedComment(models.Model):
    untouched_file_path = models.CharField("path",max_length=1024,null=False,default="")
    untouched_file_hashcode = models.CharField("hashcode",max_length=512,null=False,default="")
    # 不是很确定 我先不管这个？
    # review_request_id  = models.PositiveIntegerField(max_length=100),

    # review_request_id=models.ForeignKey(ReviewRequest, verbose_name=_('reviewrequest untouchedcomment'),
    #                              related_name="reviewrequest untouchedcomment")
                                

    class Meta:
        db_table = 'fileviewer_untouchedcomment'
        # verbose_name = _('File Untouchedcomment')
        # verbose_name_plural = _('File Untouchedcomments')