import random

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import views as auth_views

from .models import Question

def index(request): 
    return render(request,'quiz/index.html')

def start(request):
    questions_ids = list(Question.objects.values('id'))
    questions_ids = list(map(lambda x: x["id"], questions_ids))

    questions_selected = random.sample(questions_ids,3)
    first_question = questions_selected.pop()

    request.session['questions'] = questions_selected
    return redirect(question, question_id=first_question)

def question(request, question_id):

    if request.method == "GET": 
        question = Question.objects.get(id=question_id)
        return render(request,'quiz/quiz.html', {'question': question})

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
