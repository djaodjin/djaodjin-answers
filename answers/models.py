# Copyright (c) 2017, DjaoDjin inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from . import settings
from .compat import GenericForeignKey, GenericRelation
from .managers import FollowManager


class Follow(models.Model):
    """
    A relationship intended for a User to follow comments on a Question.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='user_id')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')
    time_stamp = models.DateTimeField(editable=False, auto_now_add=True)

    objects = FollowManager()

    class Meta:
        db_table = 'follows'
        unique_together = (('user', 'content_type', 'object_id'),)

    def __unicode__(self):
        return u'%s follows %s' % (self.user, self.object)


class Question(models.Model):
    """
    A Question that was submitted to the forum. Votes and Followers
    can be associated to a Question.
    """

    class Meta:
        ordering = ('-submit_date',)

    slug = models.SlugField(unique=True)
    submit_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column='user_id', null=True)
    referer = models.TextField(verbose_name=_('Referer'), blank=True, null=True)
    title = models.CharField(verbose_name=_('Title'), max_length=255)
    text = models.TextField(verbose_name=_('Text'),
                     help_text=_("Enter your question here"))
    votes = GenericRelation('voting.Vote',
        object_id_field="object_id", content_type_field="content_type")
    followers = GenericRelation(Follow,
        object_id_field="object_id", content_type_field="content_type")

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('answers_detail', (), {'pk': self.id})


