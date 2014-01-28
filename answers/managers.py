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

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

UserModel = get_user_model()

class FollowManager(models.Manager):

    def get_followers(self, question):
        """
        Get a list of followers for a Question.
        """
        ctype = ContentType.objects.get_for_model(question)
        return UserModel.objects.filter(
            follow__object_id=question._get_pk_val(),
            follow__content_type=ctype)


    def subscribe(self, user, question):
        """
        Subscribe a User to changes to a Question.
        """
        ctype = ContentType.objects.get_for_model(question)
        try:
            follow = self.get(user=user, content_type=ctype,
                              object_id=question._get_pk_val())
        except models.ObjectDoesNotExist:
            self.create(user=user, content_type=ctype,
                        object_id=question._get_pk_val())


    def unsubscribe(self, user, question):
        """
        Unsubscribe a User from changes to a Question.
        """
        ctype = ContentType.objects.get_for_model(question)
        try:
            follow = self.get(user=user, content_type=ctype,
                              object_id=question._get_pk_val())
            follow.delete()
        except models.ObjectDoesNotExist:
            pass

