import random, re, logging
from typing import Any
from urllib.parse import urlencode

from django.contrib.auth.views import LoginView
from django.core.serializers import serialize, deserialize
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, reverse
from django.views.generic import DetailView, ListView, View, RedirectView, TemplateView
from django.views.generic.base import ContextMixin

from .forms import QuestionFormSet, SurveyForm
from .models import Choice, GameSession, Question, Answer, Survey

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
    pattern_name = 'question'

    def get_random_survey_from_topic(self,topic):
        surveys = list(Survey.objects.filter(
                topic=topic,
                status=1))                              # Only accepted surveys
        return None if not surveys else random.choice(surveys)

    def get_redirect_url(self, *args, **kwargs):
        topic = self.request.POST.get('topic')
        survey = self.get_random_survey_from_topic(topic)

        if not survey:
            return "/?failed=1"

        return reverse(self.pattern_name, kwargs={"id":survey.id})

class QuestionView(ContextMixin,View):
    """
    This view is the heart of the app, provides the quiz, and stores 
    into session data the answers of the users.
    """
    def setup(self, request, *args,**kwargs):
        """ Create the context on initialization. """
        super().setup(request,*args,**kwargs)
        self.survey_id = kwargs.get('id')
        self.context = self.get_context_data(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ready'] = True
        
        if not self.request.GET.get('ready'):
            survey = Survey.objects.get(pk=self.survey_id)
            context['ready'] = False
            questions = [q.id for q in survey.questions]
            self.request.session['questions'] = questions

        if (q :=self.request.GET.get('question')):
            context['question'] = Question.objects.get(pk=q)
        elif (qs := self.request.session['questions']):
            question = qs.pop(0)
            context['question'] = Question.objects.get(pk=question)
            self.request.session['questions'] = qs

        query_prms = {
            'ready': 1,
            'question': context['question'].id,
        }

        context['question_url'] = f"?{urlencode(query_prms)}"
        
        return context

    def get(self, request, *args, **kwargs):
        return render(request, 'quiz/quiz.html', self.context)

    def post(self, request, *args, **kwargs):
        if request.POST.get('ready'):
            return self.get(request, *args, **kwargs)

        # answers = request.session.pop('answers')
        # answers.append((
        #     request.POST.get('question_id'),
        #     request.POST.get('choice'),
        #     request.POST.get('timerVal')
        # ))
        # request.session['answers'] = answers
        return self.get(request)

class EndView(RedirectView):
    """ 
    Validate the data in the session and stores it into database. Notice 
    that if the user reach this page without complete the quiz, will be
    redirected to startView.
    """
    pattern_name = 'results'

    def validate_game_session(self) -> bool:
        game_results = self.request.session.pop("answers")
        if not game_results:
            return False

        game_session = deserialize('json',self.request.session.get("game_session"))
        game_session = next(game_session).object
        game_session.save()
        
        self.request.session["game_session"] = game_session.id

        for question_id, choice_id, timer_val in game_results:
            try:
                choice = Choice.objects.get(pk=choice_id)
            except ObjectDoesNotExist:
                # When time runs out
                choice = None
            answer = Answer.new_answer(game_session,
                    Question.objects.get(pk=question_id),
                    choice,
                    timer_val)
            answer.save()

        return True
    
    def get_redirect_url(self, *args, **kwargs):
        if not self.validate_game_session():
            return '/'

        return super().get_redirect_url(*args, **kwargs)

class ResultsView(TemplateView):
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
