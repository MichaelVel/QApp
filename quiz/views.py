import random
import re
from typing import Any
import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from django.utils import timezone
from django.views import View
from django.views.generic.base import TemplateView

from .forms import QuestionFormSet, SurveyForm
from .models import Choice, Question, Answer, Survey

class IndexView(TemplateView):
    template_name = 'quiz/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['survey'] = SurveyForm()
        context['pop_up_login'] = False
        context['failed_load_game'] = False
        
        init_button_request = self.request.GET.get('next')
        if init_button_request == '/quiz/start':
            context['pop_up_login'] = True
            pass
        logging.debug(context)
        return context

@login_required(redirect_field_name='next',login_url="/")
def start(request):
    questions_ids = list(Question.objects.values('id'))
    questions_ids = list(map(lambda x: x["id"], questions_ids))

    questions_selected = random.sample(questions_ids,3)
    first_question = questions_selected.pop()

    last_session = Answer.objects.get_last_session(request.user.id)

    request.session['game_ended'] = False 
    request.session['questions'] = questions_selected
    request.session['game_session'] = last_session + 1
    request.session['answers'] = []
    return redirect('question', question_id=first_question)

class CreateSurveyView(TemplateView):
    template_name = 'quiz/create-survey.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(CreateSurveyView, self).get_context_data(**kwargs)
        context['question_formset'] = QuestionFormSet(prefix='question')
        context['survey'] = SurveyForm()
        return context

    def process_request(self,request) -> dict[str,dict[str,Any]]:
        form_data = {
                'survey' : {
                    'topic': request.POST['topic'],
                    'user': request.user,
                },
        }

        for key in request.POST:
            if 'question' not in key:
                continue
            question = re.search(r'(question-\d+)-', key).group(1)
            form_data.setdefault(question, dict())
            
            if 'question_text' in key:
                form_data[question]['question_text'] = request.POST[key]

            if 'choice' not in key:
                continue

            if 'choice_text' in key:
                choice = re.search(r'(choice-\d+)-', key).group(1)
                form_data[question].setdefault(choice, {'is_correct': False})
                form_data[question][choice]['choice_text'] = request.POST[key]

            if 'choice_set' in key:
                correct_choice = request.POST[key]
                form_data[question].update({correct_choice:{'is_correct':True}})

        return form_data

    def post(self, request, *args, **kwargs):
        form_data = self.process_request(request)
        form_data = Survey.from_form(form_data)
        form_data = Question.from_form(form_data)
        form_data = Choice.from_form(form_data)
        return redirect('index')

    


class QuestionView(View):
    def get(self,request,question_id):
        question = Question.objects.get(id=question_id)
        return render(request,'quiz/quiz.html', {'question': question})

    def post(self,request,question_id):
        if request.session['game_ended']:
            return redirect('index')

        # Store the answers in cache
        answers = request.session.get('answers')
        answers.append(
            (question_id,
            request.POST.get('choice'),
            request.POST.get('timerVal'))
        )

        request.session['answers'] = answers

        # Retrieve the next question
        questions: list[int] = request.session['questions']

        if not questions:
            request.session['game_ended'] = True 
            return redirect('end')

        question_id = questions.pop()
        request.session['questions'] = questions

        return self.get(request,question_id)


def end(request):
    """
    Check the answers after the game. If everything is ok stores the
    answers into the database.
    """
    game_results = request.session.get("answers")
    game_session = request.session.get("game_session")
   
    if not game_results:
        return HttpResponseNotFound(b"hello")

    for question_id, choice_id, timer_val in game_results:
        try:
            choice = Choice.objects.get(pk=choice_id)
        except ObjectDoesNotExist:
            # When time runs out
            choice = None

        answer = Answer(session=game_session,
                 question = Question.objects.get(pk=question_id),
                 user= request.user,
                 choice = choice,
                 pub_date=timezone.now(),
                 time=timer_val)
        answer.save()

    # Make sure is not possible to store the same answers in the database
    del request.session["answers"]

    return redirect('results')


class ResultsView(TemplateView):
    template_name = "quiz/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['score'] = Answer.objects.score(
                self.request.user.id, 
                self.request.session['game_session'])
        context['top5'] = Answer.objects.top5_scores()
        return context
