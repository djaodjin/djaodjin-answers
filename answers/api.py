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

from rest_framework import generics, status
from rest_framework.response import Response

from .mixins import QuestionMixin
from .models import Follow, Vote
from .serializers import QuestionSummarySerializer


class FollowAPIView(QuestionMixin, generics.CreateAPIView):
    """
    Follow an answer

    The authenticated user making the request will receive notification
    whenever someone comments on the answer.

    **Tags**: answers

    **Examples**

    .. code-block:: http

         POST /api/suppliers/water-use/follow/ HTTP/1.1

    responds

    .. code-block:: json

        {
            "slug": "water-user",
            "title": "How to reduce water usage?"
        }
    """
    serializer_class = QuestionSummarySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(QuestionSummarySerializer().to_representation(
            self.get_object()), status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated():
            Follow.objects.subscribe(self.get_object(), user=self.request.user)


class UnfollowAPIView(QuestionMixin, generics.CreateAPIView):
    """
    Unfollow an answer

    The authenticated user making the request will stop receiving notification
    whenever someone comments on the answer.

    **Tags**: answers

    **Examples**

    .. code-block:: http

         POST /api/suppliers/water-use/unfollow/ HTTP/1.1

    responds

    .. code-block:: json

        {
            "slug": "water-user",
            "title": "How to reduce water usage?"
        }
    """
    serializer_class = QuestionSummarySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(QuestionSummarySerializer().to_representation(
            self.get_object()), status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated():
            Follow.objects.unsubscribe(
                self.get_object(), user=self.request.user)


class UpvoteAPIView(QuestionMixin, generics.CreateAPIView):
    """
    Upvote an answer

    The authenticated user making the request indicates their support
    for the answer.

    **Tags**: answers

    **Examples**

    .. code-block:: http

         POST /api/suppliers/water-use/upvote/ HTTP/1.1

    responds

    .. code-block:: json

        {
            "slug": "water-user",
            "title": "How to reduce water usage?"
        }
    """
    serializer_class = QuestionSummarySerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated():
            Vote.objects.vote_up(self.get_object(), user=self.request.user)


class DownvoteAPIView(QuestionMixin, generics.CreateAPIView):
    """
    Downvote an answer

    The authenticated user making the request indicates their opposition
    to the answer.

    **Tags**: answers

    **Examples**

    .. code-block:: http

         POST /api/suppliers/water-use/downvote/ HTTP/1.1

    responds

    .. code-block:: json

        {
            "slug": "water-user",
            "title": "How to reduce water usage?"
        }
    """
    serializer_class = QuestionSummarySerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated():
            Vote.objects.vote_down(self.get_object(), user=self.request.user)
