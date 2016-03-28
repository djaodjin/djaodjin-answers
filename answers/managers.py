# Copyright (c) 2014, DjaoDjin inc.
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

from .compat import get_user_model


class FollowManager(models.Manager):

    @staticmethod
    def get_followers(question):
        """
        Get a list of followers for a Question.
        """
        ctype = ContentType.objects.get_for_model(question)
        object_id = question.id
        return get_user_model().objects.filter(
            follow__object_id=object_id, follow__content_type=ctype)

    def subscribe(self, user, question):
        """
        Subscribe a User to changes to a Question.
        """
        ctype = ContentType.objects.get_for_model(question)
        object_id = question.id
        try:
            self.get(user=user, content_type=ctype, object_id=object_id)
        except models.ObjectDoesNotExist:
            self.create(user=user, content_type=ctype,
                        object_id=object_id)

    def unsubscribe(self, user, question):
        """
        Unsubscribe a User from changes to a Question.
        """
        ctype = ContentType.objects.get_for_model(question)
        object_id = question.id
        try:
            follow = self.get(user=user, content_type=ctype,
                              object_id=object_id)
            follow.delete()
        except models.ObjectDoesNotExist:
            pass

