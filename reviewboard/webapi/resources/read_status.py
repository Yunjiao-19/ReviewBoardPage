from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
import logging
from djblets.webapi.decorators import (webapi_login_required,
                                       webapi_response_errors,
                                       webapi_request_fields)
from reviewboard.webapi.decorators import webapi_check_local_site, webapi_check_login_required
from djblets.webapi.errors import (DOES_NOT_EXIST, INVALID_FORM_DATA,
                                   NOT_LOGGED_IN, PERMISSION_DENIED)
from djblets.webapi.fields import (BooleanFieldType,
                                   ChoiceFieldType,
                                   DateTimeFieldType,
                                   DictFieldType,
                                   IntFieldType,
                                   ResourceFieldType,
                                   ResourceListFieldType,
                                   StringFieldType)
from reviewboard.webapi.errors import (COMMIT_ID_ALREADY_EXISTS,
                                       INVALID_CHANGE_NUMBER,
                                       NOTHING_TO_PUBLISH,
                                       PUBLISH_ERROR,
                                       REPO_INFO_ERROR)
from reviewboard.webapi.base import ImportExtraDataError, WebAPIResource
from reviewboard.webapi.mixins import MarkdownFieldsMixin
from reviewboard.webapi.resources import resources
from reviewboard.reviews.models import Group, ReviewRequest, ReadStatus
from djblets.util.decorators import augment_method_from
import json

logger = logging.getLogger(__name__)


class ReadStatusResource(MarkdownFieldsMixin, WebAPIResource):
    model = ReadStatus
    name = 'read_status'
    policy_id = 'read_status'
    model_parent_key = 'review_request'

    singleton = True

    fields = {
        'user_id': {
            'type': IntFieldType,
            'description': 'The numeric ID of the review request viewer.',
        },
        'review_request_id': {
            'type': IntFieldType,
            'description': 'The numeric ID of the review request.',
        },
        'revision_id': {
            'type': IntFieldType,
            'description': 'The numeric ID of the revision.',
        },
        'file_name': {
            'type': StringFieldType,
            'description': 'The name of the file whose read status is updated.',
        },
        'status': {
            'type': IntFieldType,
            'description': 'The read status, 0-unread, 1-tentatively read, 2-read',
        }
    }

    allowed_methods = ('PUT', 'POST', 'GET')

    CREATE_UPDATE_OPTIONAL_FIELDS = {
        'timestamp': {
            'type': DateTimeFieldType,
            'description': 'The timestamp of the ',
        },

        'extra_data': {
            'type': DictFieldType,
            'description': 'Extra data of the read status request.'
        }

    }

    @webapi_check_local_site
    @webapi_login_required
    @webapi_response_errors(COMMIT_ID_ALREADY_EXISTS, DOES_NOT_EXIST,
                            INVALID_CHANGE_NUMBER, INVALID_FORM_DATA,
                            NOT_LOGGED_IN, PERMISSION_DENIED, PUBLISH_ERROR)
    @webapi_request_fields(
        optional={},
        allow_unknown=True,
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new entry in ReadStatus table. First check if the review
        request exists in the ReviewRequest database, if so, then create 
        a row in ReadStatus table with the review_request_id, along with 
        revision_id, file_name, status provided in the request body.  
        """
        try:
            review_request = resources.review_request.get_object(\
                                                request, *args, **kwargs)
        except ObjectDoesNotExist:
            return DOES_NOT_EXIST

        review_request_id = review_request.display_id
        read_status = ReadStatus.objects.create(
            user_id=request.user.id,
            review_request_id=review_request_id,
            revision_id=json.loads(request.body)['revision_id'],
            file_name=json.loads(request.body)['file_name'],
            status=json.loads(request.body)['status'],
        )

        read_status.save()

        return 201, {
            self.item_result_key: read_status,
        }

read_status_resource = ReadStatusResource()
