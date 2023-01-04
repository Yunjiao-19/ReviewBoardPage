from __future__ import unicode_literals

from django.db import models
from django_evolution.mutations import AddField


MUTATIONS = [
    AddField('Review', 'commit_message_comments', models.ManyToManyField, related_model='reviews.CommitMessageComment'),
]