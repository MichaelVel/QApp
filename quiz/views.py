import random

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import views as auth_views
from django.views import View

from .models import Question,Answer

def index(request): 
    return render(request,'quiz/index.html')

def start(request):
    questions_ids = list(Question.objects.values('id'))
    questions_ids = list(map(lambda x: x["id"], questions_ids))

    questions_selected = random.sample(questions_ids,3)
    first_question = questions_selected.pop()

    last_session = Answer.sessions.get_last_session(request.user.id)

    if not last_session:
        last_session = 0


    request.session['questions'] = questions_selected
    request.session['game_session'] = last_session + 1
    request.session['answers'] = []
    return redirect('question', question_id=first_question)


class QuestionView(View):
    def get(self,request,question_id):
        question = Question.objects.get(id=question_id)
        return render(request,'quiz/quiz.html', {'question': question})

    def post(self,request,question_id):
        # Store the answers in cache
        answers = request.session['answers']
        answers.append((question_id,
            request.POST.get('choice'),
            request.POST['timerVal']))

        request.session['answers'] = answers

        # Retrieve the next question
        questions: list[int] = request.session['questions']

        if not questions:
            return redirect(end)

        question_id = questions.pop()
        request.session['questions'] = questions
        question = Question.objects.get(id=question_id)

        return render(request, 'quiz/quiz.html', {'question': question})


def end(request):
    return HttpResponse("Finished")

def results(request):
    pass
