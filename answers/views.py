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

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from haystack.query import SearchQuerySet
import notification.models as notification
from voting.views import vote_on_object

from .managers import UserModel
from .models import Follow, Question
from .forms import QuestionNewForm
from .signals import on_answer_posted

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


@require_GET
def question_search(request, limit=10):
    query = request.GET.get('q', None)

    results = None
    if query:
        results = SearchQuerySet().models(Question).filter_or(content=query)
        if limit:
            results = results[:int(limit)]

    return render(request, template_name='answers/question_search.html',
                  dictionary={'results': results, 'query': query})


@login_required
def question_new(request):
    """
    Create a new question.
    """
    referer = request.GET.get("referer", None)

    if request.method == 'POST':
        question_form = QuestionNewForm(request.POST, prefix='question')
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.user = request.user
            question.save()
            Follow.objects.subscribe(request.user, question)

            messages.success(request, _("Thank you for your question !"))

            # Send notification to the staff that a Question was created.
            try:
                users_to_notify = UserModel.objects.filter(is_staff=True)
                notification.send(
                    users_to_notify, "question_new", {'question': question})
            except:
                LOGGER.error("There was a problem notifiying staff "
                             "about creation of question #%d.", question.id)

            return redirect(question)
    else:
        question_form = QuestionNewForm(initial={'referer': referer},
                                        prefix='question')

    return render(request, template_name='answers/question_new.html',
                  dictionary={'question_form': question_form})


@login_required
@require_POST
def question_vote(request, question_id, direction):
    question = get_object_or_404(Question, id=question_id)

    # Auto subscribe User when he/she upvoted a question.
    if direction == 'up':
        Follow.objects.subscribe(request.user, question)
        messages.success(request,
            _('You will now receive an e-mail for new comments on "%s".'
              % question.title))

    return vote_on_object(
        request, model=Question,
        direction=direction,
        object_id=question_id,
        template_object_name='vote',
        template_name='answers/link_confirm_vote.html',
        allow_xmlhttprequest=True)


@login_required
@require_POST
def question_follow(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    Follow.objects.subscribe(request.user, question)
    messages.success(request,
        _('You will now receive an e-mail for new comments on "%s".'
          % question.title))
    return redirect(question)


@login_required
@require_POST
def question_unfollow(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    Follow.objects.unsubscribe(request.user, question)
    messages.success(request,
        _('You will no longer receive e-mails for additional comments on "%s".'
          % question.title))
    return redirect(question)
