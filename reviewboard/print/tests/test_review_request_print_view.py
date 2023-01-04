from reviewboard.testing import TestCase
from reviewboard.reviews.models import (BaseComment, GeneralComment,
                                        StatusUpdate)

class ReviewRequestPrintViewTests(TestCase):

    fixtures = ['test_users', 'test_scmtools', 'test_site']

    def _get_response(self):
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)
        diffset = self.create_diffset(review_request, revision=1)
        self.create_filediff(
            diffset,
            source_file='/diffutils.py',
            dest_file='/diffutils.py',
            source_revision='6bba278',
            dest_detail='465d217',
            diff=(
                b'diff --git a/diffutils.py b/diffutils.py\n'
                b'index 6bba278..465d217 100644\n'
                b'--- a/diffutils.py\n'
                b'+++ b/diffutils.py\n'
                b'@@ -1,3 +1,4 @@\n'
                b'+# diffutils.py\n'
                b' import fnmatch\n'
                b' import os\n'
                b' import re\n'
            ))
        self.create_filediff(
            diffset,
            source_file='/readme',
            dest_file='/readme',
            source_revision='d6613f5',
            dest_detail='5b50866',
            diff=(
                b'diff --git a/readme b/readme\n'
                b'index d6613f5..5b50866 100644\n'
                b'--- a/readme\n'
                b'+++ b/readme\n'
                b'@@ -1 +1,3 @@\n'
                b' Hello there\n'
                b'+\n'
                b'+Oh hi!\n'
            ))
        self.create_filediff(
            diffset,
            source_file='/newfile',
            dest_file='/newfile',
            source_revision='PRE-CREATION',
            dest_detail='',
            diff=(
                b'diff --git a/new_file b/new_file\n'
                b'new file mode 100644\n'
                b'index 0000000..ac30bd3\n'
                b'--- /dev/null\n'
                b'+++ b/new_file\n'
                b'@@ -0,0 +1 @@\n'
                b'+This is a new file!\n'
            ))

        diffset = self.create_diffset(review_request, revision=2)
        self.create_filediff(
            diffset,
            source_file='/diffutils.py',
            dest_file='/diffutils.py',
            source_revision='6bba278',
            dest_detail='465d217',
            diff=(
                b'diff --git a/diffutils.py b/diffutils.py\n'
                b'index 6bba278..465d217 100644\n'
                b'--- a/diffutils.py\n'
                b'+++ b/diffutils.py\n'
                b'@@ -1,3 +1,4 @@\n'
                b'+# diffutils.py\n'
                b' import fnmatch\n'
                b' import os\n'
                b' import re\n'
            ))
        self.create_filediff(
            diffset,
            source_file='/readme',
            dest_file='/readme',
            source_revision='d6613f5',
            dest_detail='5b50867',
            diff=(
                b'diff --git a/readme b/readme\n'
                b'index d6613f5..5b50867 100644\n'
                b'--- a/readme\n'
                b'+++ b/readme\n'
                b'@@ -1 +1,3 @@\n'
                b' Hello there\n'
                b'+----------\n'
                b'+Oh hi!\n'
            ))
        self.create_filediff(
            diffset,
            source_file='/newfile',
            dest_file='/newfile',
            source_revision='PRE-CREATION',
            dest_detail='',
            diff=(
                b'diff --git a/new_file b/new_file\n'
                b'new file mode 100644\n'
                b'index 0000000..ac30bd4\n'
                b'--- /dev/null\n'
                b'+++ b/new_file\n'
                b'@@ -0,0 +1 @@\n'
                b'+This is a diffent version of this new file!\n'
            ))

        response = self.client.get('/r/%d/print/' % review_request.id)
        return response, review_request

    def _make_comments(self,review_request):
        review = self.create_review(review_request)

        # 1 diff comment.
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset)
        diff_comment_1 = self.create_diff_comment(review, filediff, text='diff comment',issue_opened=True, issue_status=BaseComment.DROPPED)
        diff_comment_2 = self.create_diff_comment(review, filediff, issue_opened=True, issue_status=BaseComment.RESOLVED)

        # 2 screenshot comments.
        screenshot = self.create_screenshot(review_request)
        screenshot_comment_1 = self.create_screenshot_comment(review,
                                                              screenshot, issue_opened=True, issue_status=BaseComment.DROPPED)
        screenshot_comment_2 = self.create_screenshot_comment(review,
                                                              screenshot, issue_opened=True, issue_status=BaseComment.OPEN)

        # # 3 file attachment comments.
        file_attachment = self.create_file_attachment(review_request, mimetype='application/rbtest')
        file_attachment_comment_1 = self.create_file_attachment_comment(
            review, file_attachment,diff_against_file_attachment=file_attachment,issue_opened=True, issue_status=BaseComment.DROPPED)
        file_attachment_comment_2 = self.create_file_attachment_comment(
            review, file_attachment,diff_against_file_attachment=file_attachment,issue_opened=True, issue_status=BaseComment.VERIFYING_DROPPED)
        file_attachment_comment_3 = self.create_file_attachment_comment(
            review, file_attachment,diff_against_file_attachment=file_attachment,issue_opened=True, issue_status=BaseComment.VERIFYING_RESOLVED)

        # 4 general comments.
        general_comment_1 = self.create_general_comment(review,issue_opened=True, issue_status=BaseComment.OPEN)
        general_comment_2 = self.create_general_comment(review,issue_opened=True, issue_status=BaseComment.DROPPED)
        general_comment_3 = self.create_general_comment(review,issue_opened=True, issue_status=BaseComment.DROPPED)
        general_comment_4 = self.create_general_comment(review,issue_opened=True, issue_status=BaseComment.RESOLVED)
        
        comments_code = [diff_comment_1,diff_comment_2]
        comments_ss = [screenshot_comment_1,screenshot_comment_2]
        comments_fa = [file_attachment_comment_1,file_attachment_comment_2,file_attachment_comment_3]
        comments_gen = [general_comment_1,general_comment_2,general_comment_3,general_comment_4]

        return comments_code,comments_ss,comments_fa,comments_gen


    def test_get(self):
        """Testing ReviewRequestPrintView.get"""
        response,_ = self._get_response()
        self.assertEqual(response.status_code, 200)
        print(sorted(list(response.context.keys())))

    def test_flags(self):
        """Testing ReviewRequestPrintView flags"""
        response,_ = self._get_response()
        self.assertEqual(response.context['drop_flag'],False)
        self.assertEqual(response.context['inline_flag'],False)
        self.assertEqual(response.context['issues_flag_default'],True)
        self.assertEqual(response.context['open_flag'],False)
        self.assertEqual(response.context['res_flag'],False)
        self.assertEqual(response.context['verif_flag'],False)

    def test_slider(self):
        """Testing ReviewRequestPrintView slider"""
        response,_ = self._get_response()
        self.assertEqual(response.context['slider_end'],2) #there are 2 filediffs initialized
        self.assertEqual(response.context['slider_start'],0)

    def test_issues(self):
        """Testing ReviewRequestPrintView issues"""
        response,review_request = self._get_response()
        d = response.context['issue_flag_dict']
        for val in d.values():
            self.assertEqual(val,False)
        self.assertEqual(len(response.context['issues']),0)
        self.assertEqual(response.context['issue_types']==\
            {'O': 'Open', 'R': 'Resolved', 'D': 'Dropped', 'A': 'Verifying Resolved', 'B': 'Verifying Dropped'},True)
        self.assertEqual(response.context['issues_exist'],False)
        self._make_comments(review_request)
        self.assertEqual(len(response.context['files']),3)