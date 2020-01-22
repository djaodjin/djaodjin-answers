# Copyright (c) 2020, DjaoDjin inc.
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
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import settings
from .compat import get_model_class


class FollowManager(models.Manager):

    @staticmethod
    def get_followers(question):
        """
        Get a list of followers for a Question.
        """
        return get_user_model().objects.filter(follows__question=question)

    def subscribe(self, question, user):
        """
        Subscribe a User to changes to a Question.
        """
        self.get_or_create(user=user, question=question)

    def unsubscribe(self, question, user):
        """
        Unsubscribe a User from changes to a Question.
        """
        try:
            self.get(user=user, question=question).delete()
        except models.ObjectDoesNotExist:
            pass



@python_2_unicode_compatible
class Follow(models.Model):
    """
    A relationship intended for a User to follow comments on a Question.
    """
    objects = FollowManager()

    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='user_id',
         related_name='follows', on_delete=models.CASCADE)
    question = models.ForeignKey(settings.QUESTION_MODEL,
        related_name='followers', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'question'),)

    def __str__(self):
        return u'%s follows %s' % (self.user, self.question)


def get_question_model():
    return get_model_class(settings.QUESTION_MODEL, 'QUESTION_MODEL')


@python_2_unicode_compatible
class Question(models.Model):
    """
    A Question that was submitted to the forum. Votes and Followers
    can be associated to a Question.
    """
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    slug = models.SlugField(unique=True, help_text=_(
        "unique identifier for the question. It can be used in a URL."))
    title = models.CharField(verbose_name=_('Title'), max_length=255,
        help_text=_("Short description of the question."))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='user_id',
            null=True, on_delete=models.CASCADE)
    referer = models.TextField(verbose_name=_('Referer'), blank=True, null=True)
    text = models.TextField(verbose_name=_('Text'),
                     help_text=_("Enter your question here"))

    def __str__(self):
        return self.slug


class VoteManager(models.Manager):

    def vote_up(self, question, user):
        """
        Vote a Question up by a User.
        """
        vote, created = self.get_or_create(user=user, question=question,
            defaults={'vote': Vote.UP_VOTE})
        if not created:
            vote.vote = Vote.UP_VOTE
            vote.save()

    def vote_down(self, question, user):
        """
        Vote a Question down by a User.
        """
        vote, created = self.get_or_create(user=user, question=question,
            defaults={'vote': Vote.DOWN_VOTE})
        if not created:
            vote.vote = Vote.DOWN_VOTE
            vote.save()


@python_2_unicode_compatible
class Vote(models.Model):
    """
    A vote on an question by a User.
    """
    objects = VoteManager()

    UP_VOTE = 1
    DOWN_VOTE = -1
    SCORES = (
        (UP_VOTE, u'+1'),
        (DOWN_VOTE, u'-1'),
    )

    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(settings.QUESTION_MODEL,
        related_name='votes', on_delete=models.CASCADE)
    vote = models.SmallIntegerField(choices=SCORES)

    class Meta:
        # One vote per user per Question
        unique_together = (('user', 'question'),)

    def __str__(self):
        return u'%s: %s on %s' % (self.user, self.vote, self.question)

    def is_upvote(self):
        return self.vote == self.UP_VOTE

    def is_downvote(self):
        return self.vote == self.DOWN_VOTE

