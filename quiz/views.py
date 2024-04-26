import random, re, logging
from typing import Any
from urllib.parse import urlencode

from django.contrib.auth.views import LoginView
from django.core.serializers import serialize, deserialize
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.views.generic import DetailView, ListView, View, RedirectView, TemplateView
from django.views.generic.base import ContextMixin

from .forms import QuestionFormSet, SurveyForm
from .models import Choice, Question, Answer, Survey

class IndexView(TemplateView):
    """ 
    Display the home page. In this page the user can login to the page
    and choose the topic for the game.
    """
    template_name = 'quiz/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        form = SurveyForm() 

        if not self.request.user.is_superuser:
            form.remove_test_option()

        context['survey'] = form
        context['pop_up_login'] = False
        context['failed_load_game'] = False
        
        init_button_request = self.request.GET.get('next')
        failed_login = self.request.GET.get('failed-login')
        failed_request = self.request.GET.get('failed')

        if init_button_request == '/quiz/start':
            context['pop_up_login'] = True
            context['please_login'] = True

        if failed_request:
            context['failed_load_game'] = True

        if failed_login == '1':
            context['failed_login'] = True
            context['pop_up_login'] = True

        return context

class QLoginView(LoginView):
    """ Custom login view to change the default behaviour of failed login """ 
    def form_invalid(self, form):
        return redirect('/?failed-login=1')

class CreateSurveyView(TemplateView):
    """ Simple Page to create thematic surveys. """
    template_name = 'quiz/create-survey.html'

    def get_context_data(self, **kwargs):
        context = super(CreateSurveyView, self).get_context_data(**kwargs)
        form = SurveyForm(initial={'name': ''})

        if not self.request.user.is_superuser:
            form.remove_test_option()

        context['question_formset'] = QuestionFormSet(prefix='question')
        context['survey'] = form
        return context

    def process_request(self,request) -> dict[str,Any]:
        """ 
        convert the data of the POST request into a object similar to a 
        simple JSON object.
        """
        form_data = {
                'survey' : {
                    'topic': request.POST['topic'],
                    'name': request.POST['name'],
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
        Choice.from_form(form_data)

        return redirect('surveys')

class ListSurveysView(ListView):
    model = Survey

    def get_context_data(self, **kwargs):
        context = super(ListSurveysView, self).get_context_data(**kwargs)
        form = SurveyForm(initial={'name': ''})

        if not self.request.user.is_superuser:
            form.remove_test_option()

        context['survey'] = form
        return context
    
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args,**kwargs)
        user =self.request.user

        if not user.is_superuser:
            qs = qs.filter(user=user)

        if self.request.GET:
            qs = qs.filter(topic=self.request.GET['topic'])

        return qs.order_by('-creation_date')[:10]

class SurveyDetailsView(DetailView):
    model = Survey

    def get_context_data(self, **kwargs):
        context = super(SurveyDetailsView, self).get_context_data(**kwargs)
        form = SurveyForm(initial={'name': ''})
        context['survey'] = form
        return context
    
    def post(self, request, *args, **kwargs):
        qs = self.get_queryset()
        survey = self.get_object(qs)
        status = request.POST['status']

        survey.status = status
        survey.save()

        return self.get(request, *args, *kwargs)


class StartView(RedirectView):
    """ 
    Check if exists quizzes of the topic chose by the user, then get a random
    quiz and load the game session, if not redirects to main page.  
    """
    pattern_name = 'survey'

    def get_random_survey_from_topic(self,topic):
        surveys = list(Survey.objects.filter(
                topic=topic,
                status=1))                              # Only accepted surveys
        return None if not surveys else random.choice(surveys)

    def questions_id(self, survey):
        return [q.id for q in survey.questions]

    def get_redirect_url(self, *args, **kwargs):
        topic = self.request.POST.get('topic')
        survey = self.get_random_survey_from_topic(topic)

        if not survey:
            return "/?failed=1"

        self.request.session['answers'] = {}

        return reverse(self.pattern_name, kwargs={"id":survey.id})

class SurveyView(ContextMixin, View):
    """
    This View display the get ready message with a timer, in the future it
    could have information about the survey if needed. 
    """
    def setup(self, request, *args,**kwargs):
        """ Create the context on initialization. """
        super().setup(request,*args,**kwargs)
        self.survey_id = kwargs.get('id')
        self.context = self.get_context_data(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = get_object_or_404(Survey, pk=self.survey_id)
        next_question = survey.next_question()
        context['question_url'] = f"{self.survey_id}/questions/{next_question.id}" 
        return context

    def get(self, request, *args, **kwargs):
        return render(request, 'quiz/survey.html', self.context)


class QuestionView(ContextMixin,View):
    """
    This view is the heart of the app, provides the quiz, and stores 
    into session data the answers of the users.
    """
    def setup(self, request, *args,**kwargs):
        """ Create the context on initialization. """
        super().setup(request,*args,**kwargs)
        self.survey_id = kwargs.get('s_id')
        self.question_id = kwargs.get('q_id')
        self.context = self.get_context_data(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        survey = get_object_or_404(Survey, pk = self.survey_id)
        question = get_object_or_404(Question, pk=self.question_id)

        context['question'] = question
        context['survey'] = survey
        
        return context

    def quiz_ended(self):
        answers = self.request.session.pop('answers', None)
        user = self.request.user

        if answers is None:
            return redirect('index')
        
        score = sum(n for n in answers.values())
        if user.is_authenticated:
            Answer.objects.create(
                user=user, survey=self.context['survey'], score=score)

        self.request.session['score'] = score
        return redirect('results', id = self.survey_id)

    def get(self, request, *args, **kwargs):
        return render(request, 'quiz/quiz.html', self.context)

    def post(self, request, *args, **kwargs):
        answers: dict[int, int]  = request.session.pop('answers')

        question = self.context["question"]
        score = question.score(
            int(request.POST.get('choice') or 0),
            int(request.POST.get('timerVal' or 0)))

        answers.update({question.id: score})

        request.session['answers'] = answers

class ResultsView(TemplateView):
        next_question = self.context['survey'].next_question(self.question_id)
        if next_question is None:
            return self.quiz_ended()

        return redirect('question', s_id = self.survey_id, q_id = next_question.id)

    """ 
    Display the results of the quiz and a ranking of the top scores for 
    the given quiz.
    """
    template_name = "quiz/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_session_id = self.request.session.get("game_session")
        game_session = GameSession.objects.get(pk=game_session_id)
        survey = game_session.survey
        context['score'] = game_session.score
        context['survey'] = survey
        context['top5'] = GameSession.scores.top_n_scores(5,survey)
        return context
