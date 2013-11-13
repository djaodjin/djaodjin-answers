# Copyright (c) 2013, The DjaoDjin Team
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of DjaoDjin nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY The DjaoDjin Team ''AS IS'' AND ANY
#   EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#   WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL The DjaoDjin Team LLC BE LIABLE FOR ANY
#   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#   (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#   LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Signals logic to trigger events in connected apps.
"""

from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_noop as _
from django.contrib.comments.signals import comment_was_posted
from django.db.models.signals import post_syncdb
import notification.models as notification

from .models import Follow, Question


@receiver(post_syncdb, sender=notification)
def create_notice_types(app, created_models, verbosity, **kwargs):
    notification.NoticeType.create(
        "question_new", _("New question"), _("A new question was submitted"))
    notification.NoticeType.create(
        "question_updated", _("Question updated"), _("A question was updated"))


@receiver(comment_was_posted)
def on_answer_posted(sender, comment, request, *args, **kwargs):
    # Send the 'question_updated' signal
    question_ctype = ContentType.objects.get_for_model(Question)
    if comment.content_type == question_ctype:
        question = comment.content_object
        notification.send(Follow.objects.get_followers(question),
            'question_updated', {'question': question})

        # Subscribe the commenting user to this question
        Follow.objects.subscribe(request.user, question)
