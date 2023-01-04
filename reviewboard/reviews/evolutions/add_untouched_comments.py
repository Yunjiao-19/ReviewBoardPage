from __future__ import unicode_literals

from django.db import models
from django_evolution.mutations import AddField


MUTATIONS = [
    AddField('Review', 'untouched_comments', models.ManyToManyField, related_model='reviews.UntouchedComment'),
]