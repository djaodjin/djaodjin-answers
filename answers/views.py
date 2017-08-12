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

import logging

from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic import (CreateView, ListView, TemplateView)
from django.views.generic.detail import DetailView
from haystack.query import SearchQuerySet

from . import signals
from .models import Follow, get_question_model
from .mixins import QuestionMixin
from .forms import QuestionCreateForm

LOGGER = logging.getLogger(__name__)


class QuestionDetailView(QuestionMixin, DetailView):
    """
    Generic view for a single Question.
    """

    model = get_question_model()


class QuestionListView(ListView):
    """
    Generic view of a list of Questions.
    """

    model = get_question_model()

    def get_context_data(self, **kwargs):
        context = super(QuestionListView, self).get_context_data(**kwargs)
        return context


class QuestionSearchView(TemplateView):
    """
    Search for Questions matching 'q'.
    """
    limit = 10
    model = get_question_model()
    template_name = 'answers/question_search.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionSearchView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q', None)
        results = None
        if query:
            # XXX search broken until new release of haystack compatible with
            # Django 1.6:
            #   https://github.com/toastdriven/django-haystack/issues/908
            results = SearchQuerySet().models(self.model).filter_or(
                content=query)
            if self.limit:
                results = results[:int(self.limit)]
        context.update({'results': results, 'query': query})
        return context


class QuestionCreateView(CreateView):
    """
    Create a new question.
    """

    model = get_question_model()
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
        Follow.objects.subscribe(self.object, user=self.request.user)
        return result

    def get_initial(self):
        kwargs = super(QuestionCreateView, self).get_initial()
        kwargs.update({'referer': self.request.GET.get("referer", None)})
        if self.request.user.is_authenticated():
            kwargs.update({'user': self.request.user})
        return kwargs
