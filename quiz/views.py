import random

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from django.views.generic.base import TemplateView

from .models import Choice, Question,Answer

def index(request): 
    context = {}
    if (next_val := request.GET.get('next',None)) is not None:
        context["next"] = next_val

    return render(request,'quiz/index.html', context)

@login_required(redirect_field_name='next',login_url="/")
def start(request):
    questions_ids = list(Question.objects.values('id'))
    questions_ids = list(map(lambda x: x["id"], questions_ids))

    questions_selected = random.sample(questions_ids,3)
    first_question = questions_selected.pop()

    last_session = Answer.sessions.get_last_session(request.user.id)

    request.session['game_ended'] = False 
    request.session['questions'] = questions_selected
    request.session['game_session'] = last_session + 1
    request.session['answers'] = []
    return redirect('question', question_id=first_question)


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
        context['score'] = Answer.sessions.score(
                self.request.user.id, 
                self.request.session['game_session'])
        context['top5'] = Answer.sessions.top5_scores()
        return context
