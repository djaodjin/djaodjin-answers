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

import logging

from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic import (CreateView, ListView, RedirectView,
    TemplateView, View)
from django.views.generic.detail import SingleObjectMixin, DetailView
from haystack.query import SearchQuerySet
from voting.views import vote_on_object

from answers.models import Follow, Question
from answers.forms import QuestionCreateForm
from answers import signals

LOGGER = logging.getLogger(__name__)


class QuestionDetailView(DetailView):
    """
    Generic view for a single Question.
    """

    model = Question

    def get_context_data(self, **kwargs):
        context = super(QuestionDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_following'] = Follow.objects.get_followers(
                kwargs['object']).filter(pk=self.request.user.id).exists()
        return context


class QuestionListView(ListView):
    """
    Generic view of a list of Questions.
    """

    model = Question

    def get_context_data(self, **kwargs):
        context = super(QuestionListView, self).get_context_data(**kwargs)
        return context


class QuestionSearchView(TemplateView):
    """
    Search for Questions matching 'q'.
    """
    limit = 10
    template_name = 'answers/question_search.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionSearchView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q', None)
        results = None
        if query:
            # XXX search broken until new release of haystack compatible with
            # Django 1.6:
            #   https://github.com/toastdriven/django-haystack/issues/908
            results = SearchQuerySet().models(Question).filter_or(content=query)
            if self.limit:
                results = results[:int(self.limit)]
        context.update({'results': results, 'query': query})
        return context


class QuestionCreateView(CreateView):
    """
    Create a new question.
    """

    model = Question
    form_class = QuestionCreateForm
    template_name = 'answers/question_new.html'
    prefix = 'question'

    def form_valid(self, form):
        if not self.request.user.is_authenticated():
            return self.form_invalid(form)
        result = super(QuestionCreateView, self).form_valid(form)
        messages.success(self.request, _("Thank you for your question !"))
        # Send notification to the staff that a Question was created.
        signals.question_new.send(
            sender=__name__, question=self.object, request=self.request)
        Follow.objects.subscribe(self.request.user, self.object)
        return result

    def get_initial(self):
        kwargs = super(QuestionCreateView, self).get_initial()
        kwargs.update({'referer': self.request.GET.get("referer", None)})
        if self.request.user.is_authenticated():
            kwargs.update({'user': self.request.user})
        return kwargs


class QuestionVoteView(SingleObjectMixin, View):
    """
    Vote a Question up/down
    """
    model = Question

    def post(self, request, *args, **kwargs): #pylint: disable=unused-argument
        # Auto subscribe User when he/she upvoted a question.
        self.object = self.get_object()
        direction = kwargs.get('direction', 'up')
        if direction == 'up':
            Follow.objects.subscribe(request.user, self.object)
            messages.success(request,
                _('You will now receive an e-mail for new comments on "%s".'
                  % self.object.title))

        return vote_on_object(
            request, model=Question,
            direction=direction,
            object_id=self.object.pk,
            post_vote_redirect=self.get_redirect_url(),
            template_object_name='vote',
            template_name='answers/link_confirm_vote.html',
            allow_xmlhttprequest=True)

    def get_redirect_url(self, *args, **kwargs): #pylint: disable=unused-argument
        return self.object.get_absolute_url()


class QuestionFollowView(SingleObjectMixin, RedirectView):
    """
    Start following comments on a Question
    """
    model = Question

    def get_redirect_url(self, *args, **kwargs):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        Follow.objects.subscribe(request.user, self.object)
        messages.success(request,
            _('You will now receive an e-mail for new comments on "%s".'
              % self.object.title))
        return super(QuestionFollowView, self).post(request, *args, **kwargs)


class QuestionUnfollowView(SingleObjectMixin, RedirectView):
    """
    Stop following comments on a Question
    """
    model = Question

    def get_redirect_url(self, *args, **kwargs):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        Follow.objects.unsubscribe(request.user, self.object)
        messages.success(request,
        _('You will no longer receive e-mails for additional comments on "%s".'
          % self.object.title))
        return super(QuestionUnfollowView, self).post(request, *args, **kwargs)

