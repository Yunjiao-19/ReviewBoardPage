from __future__ import unicode_literals

import fnmatch
import logging
import os
import re
import shutil
import subprocess
import tempfile

from django.contrib.sites.models import Site

from reviewboard.diffviewer.diffutils import *
from reviewboard.diffviewer.views import exception_traceback_string
from reviewboard.scmtools.core import SCMTool
from reviewboard.reviews.models.review_request import ReviewRequest
from reviewboard.scmtools.git import GitTool
from django.http import HttpResponse
from djblets.util.compat.django.template.loader import render_to_string

from reviewboard.diffviewer.models import FileUntouchedComment
from reviewboard.reviews.models import UntouchedComment
from reviewboard.reviews.models import Review
from collections import defaultdict

logger = logging.getLogger(__name__)


def extract_file_path(request, request_args, revision=None):
    """This will handle the code browser request and
    extract requested code repo file path to feed the given path to kwargs.

     Args:
        request (django.http.HttpRequest):
            The HTTP request from the client.

        request_args (dict)

       revision (int, optional):
        The revision of the diff to view. This defaults to the latest
        diff.
    """

    url_path = request.path
    if re.search("^/r/\d+/code/", url_path):
        code_path = url_path.split('code/', 1)[1]
        if not code_path.startswith('blob'):
            request_args['is_blob'] = False
            # default case: either with 'tree' or without
            if code_path.startswith('tree'):
                code_path = code_path.lstrip('tree/')
            request_args['code_path'] = code_path
        elif code_path.startswith('api/blob/'):
            request_args['is_blob'] = True
            code_path = code_path.lstrip('api/blob/')
            request_args['code_path'] = code_path
        else:
            request_args['is_blob'] = True
            code_path = code_path.lstrip('blob/')
            request_args['code_path'] = code_path
            hashcode = request.GET.get('hashcode')
            diff_url = url_path.split('code/', 1)[0] + "diff/#index_header"
            request_args['diff_url'] = diff_url
            request_args['blob_content_url'] = url_path.split('code/', 1)[
                                                   0] + "code/api/blob/" + code_path + "?hashcode=" + str(hashcode)

        request_args['revision'] = revision
    elif re.search("^/r/\d+/diff/", url_path):
        code_path = url_path.split('diff/', 1)[1]
        if 'revision' in request_args:
            code_path = code_path.split('/', 1)[1]

        if code_path.startswith('api/blob/'):
            request_args['is_blob'] = True
            code_path = code_path.lstrip('api/blob/')
            request_args['code_path'] = code_path
        else:
            raise ValueError
    else:
        # path is not correct, need to raise an value error and return 404
        raise ValueError
    pass


def get_file_tree(review_request, path, revision, modified_file_set, commit, absolute_path):
    repository = review_request.repository
    # type casting
    git_tool: GitTool = repository.get_scmtool()
    tree_data = git_tool.get_repo_directory(path, revision, commit)

    path_lst = [review_request.repository.name]
    if path:
        path_lst += path.split("/")  # for bread crumb

    # parse content
    tree = {
        "current_path": path,
        "path_list": path_lst,  # edge cases handling?
        "is_blob": False,
        "file_list": get_subtree_list(tree_data, path, modified_file_set, absolute_path)
    }
    return tree


def get_subtree_list(data, path, modified_file_set, absolute_path):
    data: str = str(data).lstrip("b'").rstrip("'")
    raw_item_lst = data.split("\\n")
    tree_lst = []
    prev_path = absolute_path.split('code/', 1)[0] + "code/"
    for item in raw_item_lst:
        # need to check if it is a valid input
        if item:
            tree_lst.append(create_file_item(item, path, modified_file_set, prev_path))

    tree_lst.sort(key = cmp_to_key(
        lambda x, y: cmp(x['type_num'],
                         y['type_num'] or cmp(x['name'],
                                               y['name']))))
    return tree_lst


def create_file_item(item, path, modified_file_set, prev_path):
    file_item = {"type": "tree", "name": item.split("\\t")[1], "is_touched": False, "hashcode": ""}
    lst = item.split("\\t")[0].split(" ")
    if str(lst[1]) == "tree":
        file_item["type"] = "tree"
        file_item["type_num"] = 1
        # file_item["is_touched"] = False
        full_name = file_item["name"]
        if path:
            full_name = path + "/" + file_item["name"]
        file_item["absolute_url"] = prev_path + "tree/" + full_name
    else:
        file_item["type"] = "blob"
        file_item["type_num"] = 2
        full_name = file_item["name"]
        if path:
            full_name = path + "/" + file_item["name"]
        if full_name in modified_file_set:
            file_item["is_touched"] = True
        else:
            file_item["is_touched"] = False
        file_item["absolute_url"] = prev_path + "blob/" + full_name + "?hashcode=" + str(lst[2])

    file_item["hashcode"] = str(lst[2])
    return file_item


def get_original_code_file(review_request, path, modified_file_set, hashcode):
    repository = review_request.repository
    # type casting
    git_tool: GitTool = repository.get_scmtool()
    encoding, original_file = convert_to_unicode(str(git_tool.get_file_by_hashcode(path, hashcode)),
                                                 repository.get_encoding_list())
    # original_file = convert_line_endings(original_file)

    path_lst = [review_request.repository.name]
    path_lst += path.split("/")
    blob = {
        "current_path": path,
        "path_list": path_lst,
        "is_blob": True,
        "content": convert_to_line_list(original_file),
        "is_touched": False,
        "hashcode": hashcode
    }

    if path in modified_file_set:
        blob["is_touched"] = True

    return blob


def convert_to_line_list(data):
    data = str(data).lstrip("b'").rstrip("'")
    lines = data.split("\\n")
    if not lines[-1]:
        return lines[:-1]
    else:
        return lines


def get_bread_crumbs(path_list, absolute_path):
    """
    return a list of absolute path for the breadcrumb
    """
    prev_path = absolute_path.split('code/', 1)[0] + "code/tree/"
    breadcrumbs = get_absolute_path_list(prev_path, path_list)
    return {'breadcrumbs': breadcrumbs}


def get_absolute_path_list(prev_path, code_path_list):
    breadcrumbs = []
    for index, element in enumerate(code_path_list):
        obj = {
            'url': prev_path + '/'.join(code_path_list[1:index + 1]),
            'name': element,
            'tail': True if index == len(code_path_list) - 1 else False
        }
        breadcrumbs.append(obj)

    return breadcrumbs


class BlobRenderer(object):
    default_template_name = 'reviews/code_viewer_fragment.html'

    def __init__(self, blob_file, chunk_index=None, highlighting=False,
                 collapse_all=True, lines_of_context=None, context=None,
                 template_name=default_template_name, show_deleted=False):
        self.blob_file = blob_file
        self.chunk_index = chunk_index
        self.highlighting = highlighting
        self.collapse_all = collapse_all
        self.lines_of_context = lines_of_context
        self.extra_context = context or {}
        self.template_name = template_name
        self.num_chunks = 0
        self.show_deleted = show_deleted

        if self.lines_of_context and len(self.lines_of_context) == 1:
            # If we only have one value, then assume it represents before
            # and after the collapsed header area.
            self.lines_of_context.append(self.lines_of_context[0])

    def render_to_response(self, request):
        """Renders the diff to an HttpResponse."""
        return HttpResponse(self.render_to_string(request))

    def render_to_string(self, request):
        """
        """
        populate_blob_files(self.blob_file, request=request, context=self.extra_context)

        return render_to_string(template_name=self.template_name,
                                context=self.make_context())

    def make_context(self):
        """Creates and returns context for a diff render."""
        context = self.extra_context.copy()
        return context


def populate_blob_files(blob_file, request, context):
    chunk_generator = get_blob_chunk_generator(request=request, blob_file=blob_file, context=context)
    chunks = chunk_generator.get_chunks_blob()
    context.update({
        'chunks': chunks,
        'num_chunks': len(chunks),
    })


_blob_renderer_class = BlobRenderer


def get_blob_renderer(*args, **kwargs):
    return _blob_renderer_class(*args, **kwargs)


class BlobChunkGenerator(object):

    def __init__(self, request, blob_file, context, enable_syntax_highlighting=True):
        self.request = request
        self.extra_context = context
        self.blob = blob_file
        # self.review_request = self.extra_context["review_request"]
        # self.repository = self.review_request.get_repository()
        # self.tool = self.repository.get_scmtool()
        self._chunk_index = 0

    def get_chunks_blob(self):
        content = self.blob["content"]
        num_lines = len(content)

        return [self._new_chunk(content) for _ in range(num_lines)]

    def _new_chunk(self, content):
        chunk = {
            'index': self._chunk_index,
            'lines': content[self._chunk_index],
        }
        self._chunk_index += 1
        return chunk


_generator = BlobChunkGenerator


def get_blob_chunk_generator(*args, **kwargs):
    """Returns a DiffChunkGenerator instance used for generating chunks."""
    return _generator(*args, **kwargs)


def enrich_untouched_in_comments_context_by_review_request(review_request, anchor_starting, modified_file_set,
                                                           request_path, context):
    def create_file_element(filepath, hash):
        file_element = {
            "path": filepath,
            "index": anchor_starting,
            # it takes a need router
            "blob_content_url":
                request_path + "api/blob/{}?hashcode={}".format(filepath, hash),
            "anchor_pt": anchor_starting,
            "hashcode": hash,
            "is_touched": True if filepath in modified_file_set else False,
        }
        return file_element

    diff_context = context['diff_context']

    review_list = Review.objects.filter(review_request_id=review_request.display_id)

    total_file_list = []
    total_untouched_comment_mp = defaultdict(list)
    for review in review_list:
        sub_untouched_comment_mp, file_lst = get_untouched_comments_by_review(review.id, review_request)
        for file in file_lst:
            if file not in total_file_list:
                total_file_list.append(file)

        for key in sub_untouched_comment_mp:
            total_untouched_comment_mp[key] += sub_untouched_comment_mp[key]

    file_lst = []
    for file_tuple in total_file_list:
        file_lst.append(create_file_element(file_tuple[0], file_tuple[1]))
        anchor_starting += 1

    for key in total_untouched_comment_mp:
        total_untouched_comment_mp[key].sort(key=cmp_to_key(
            lambda x, y: cmp(x['firstline'],
                             y['firstline'] or cmp(x['num_lines'],
                                                   y['num_lines']) or cmp(x["timestamp"],
                                                                          y["timestamp"]))))
    context['untouched_files'] = file_lst
    context['untouched_comments'] = total_untouched_comment_mp
    diff_context['untouched_files'] = file_lst
    diff_context['untouched_comments'] = total_untouched_comment_mp


def get_untouched_comment_file(comment):
    file_id = comment.untouchedfile_id
    return FileUntouchedComment.objects.get(id=file_id)


def get_untouched_comments_by_review(review_id, review_request):
    def tuplefy_file(file):
        return str(file.untouched_file_path), str(file.untouched_file_hashcode)

    def convert_comment(comment, file, reviewid=None):
        untouched_file_comment = {
            "review_id": reviewid,
            "review_request_id": comment.get_review_request().id,
            "file_path": file.untouched_file_path,
            "file_hashcode": file.untouched_file_hashcode,
            "content": comment.text,
            "timestamp": comment.timestamp,
            "firstline": comment.first_line,
            "num_lines": comment.num_lines,
            "extra_data": comment.extra_data,
            "comment_type": "untouched_comments",
            "issue_opened": comment.issue_opened,
            "issue_status": comment.issue_status,
            "reply_to_id": comment.reply_to_id,
            "rich_text": False if comment.rich_text == 1 else True,
            "replies": None,  # tentatively
            "url": review_request.get_absolute_url()
        }
        return untouched_file_comment

    review = Review.objects.get(id=review_id)
    untouched_comments = review.untouched_comments.all()
    untouched_comments_mp = defaultdict(list)
    untouched_file_tuple_lst = []
    for untouched_comment in untouched_comments:
        untouched_file = get_untouched_comment_file(untouched_comment)
        if not untouched_file or tuplefy_file(untouched_file) not in untouched_file_tuple_lst:
            untouched_file_tuple_lst.append(tuplefy_file(untouched_file))
        untouched_comments_mp[untouched_file.untouched_file_path].append(
            convert_comment(untouched_comment, untouched_file, review_id))
    return untouched_comments_mp, untouched_file_tuple_lst


# def get_untouched_comments_by_review_request(review_request_id):
#     """
#         obtain review list by review request
#         obtain comments by reivew
#         obtain files by comments
#     """
#
#     untouched_comments = {
#         "review_request_id": review_request_id
#     }
#     comments = []
#     review_list = Review.objects.filter(review_request_id=review_request_id)
#     for review in review_list:
#         untouched_comment = get_untouched_comments_by_review(review.id)
#         comments.append(untouched_comment)
#     untouched_comments.update({
#         "comments": comments
#     })
#     return untouched_comments
def add_blob_comments(filepath, hashcode, context, review_request):
    comments_by_file_mp = get_untouched_comments_by_file(filepath, hashcode, review_request)
    context['untouched_comments'] = comments_by_file_mp
    context['blob_context'] = {}
    blob_context = context['blob_context']
    blob_context['untouched_comments'] = comments_by_file_mp
    pass


def get_untouched_comments_by_file(filepath, hashcode, review_request):
    def convert_comment(path, file_hashcode, comment):
        untouched_comment_object = {
            "review_id": comment.get_review().id,
            "review_request_id": comment.get_review_request().id,
            "file_path": path,
            "file_hashcode": file_hashcode,
            "content": comment.text,
            "timestamp": comment.timestamp,
            "firstline": comment.first_line,
            "num_lines": comment.num_lines,
            "extra_data": comment.extra_data,
            "comment_type": "untouched_comments",
            "issue_opened": comment.issue_opened,
            "issue_status": comment.issue_status,
            "reply_to_id": comment.reply_to_id,
            "rich_text": False if comment.rich_text == 1 else True,
            "replies": None,  # tentatively
            "url": review_request.get_absolute_url()
        }
        return untouched_comment_object

    untouched_file = FileUntouchedComment.objects.filter(untouched_file_path=filepath,
                                                         untouched_file_hashcode=hashcode)

    if not untouched_file:
        return []
    untouched_file = untouched_file[0]
    untouched_comments = UntouchedComment.objects.filter(untouchedfile=untouched_file)
    comments_by_file_mp = defaultdict(list)
    for untouched_comment in untouched_comments:
        comments_by_file_mp[filepath].append(convert_comment(filepath, hashcode, untouched_comment))

    for key in comments_by_file_mp:
        comments_by_file_mp[key].sort(key=cmp_to_key(
            lambda x, y: cmp(x['firstline'],
                             y['firstline'] or cmp(x['num_lines'],
                                                   y['num_lines']) or cmp(x["timestamp"],
                                                                          y["timestamp"]))))
    return comments_by_file_mp


def get_chunks_in_range(content, first_line, num_line):
    def create_chunk(idx):
        chunk = {
            'index': idx,
            'lines': content[idx]
        }
        return chunk

    for index in range(first_line, first_line + num_line):
        yield create_chunk(index)


def build_untouched_comment_fragments(
        untouched_comments,
        context,
        review_request,
        comment_template_name='reviews/review_untouched_fragment.html',
        error_template_name='diffviewer/diff_fragment_error.html',
        request=None):
    comment_entries = []
    had_error = False
    siteconfig = SiteConfiguration.objects.get_current()

    for untouched_comment in untouched_comments:
        try:
            repository = review_request.repository
            git_tool = repository.get_scmtool()
            _, original_file = convert_to_unicode(
                str(git_tool.get_file_by_hashcode(untouched_comment.untouchedfile.untouched_file_path,
                                                  untouched_comment.untouchedfile.untouched_file_hashcode)),
                repository.get_encoding_list())
            code = convert_to_line_list(original_file)

            first_line = max(1, untouched_comment.first_line)
            # last_line = min(untouched_comment.last_line + lines_of_context[1], max_line)
            last_line = untouched_comment.last_line
            num_lines = last_line - first_line + 1

            chunks = list(get_chunks_in_range(code, first_line, num_lines))

            comment_context = {
                'comment': untouched_comment,
                'chunks': chunks,
                'domain': Site.objects.get_current().domain,
                'domain_method': siteconfig.get('site_domain_method'),
                'first_line': first_line,
            }
            comment_context.update(context)
            content = render_to_string(template_name=comment_template_name,
                                       context=comment_context,
                                       request=request)
        except Exception as e:
            content = exception_traceback_string(
                None, e, error_template_name, {
                    'comment': untouched_comment,
                    'file': {
                        'depot_filename': untouched_comment.untouchedfile.untouched_file_path,
                    },
                    'domain': Site.objects.get_current().domain,
                    'domain_method': siteconfig.get("site_domain_method"),
                })

            # It's bad that we failed, and we'll return a 500, but we'll
            # still return content for anything we have. This will prevent any
            # caching.
            had_error = True
            chunks = []

        comment_entries.append({
            'comment': untouched_comment,
            'html': content,
            'chunks': chunks,
        })

    return had_error, comment_entries
