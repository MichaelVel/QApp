import random, re, logging
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize, deserialize
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import ContextMixin, RedirectView, TemplateView

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
        context['survey'] = SurveyForm()
        context['pop_up_login'] = False
        context['failed_load_game'] = False
        
        init_button_request = self.request.GET.get('next')
        failed_request = self.request.GET.get('failed')

        if init_button_request == '/quiz/start':
            context['pop_up_login'] = True

        if failed_request:
            context['failed_load_game'] = True

        return context

class CreateSurveyView(TemplateView):
    """ Simple Page to create thematic surveys. """
    template_name = 'quiz/create-survey.html'

    def get_context_data(self, **kwargs):
        context = super(CreateSurveyView, self).get_context_data(**kwargs)
        context['question_formset'] = QuestionFormSet(prefix='question')
        context['survey'] = SurveyForm()
        return context

    def process_request(self,request) -> dict[str,dict[str,Any]]:
        """ 
        convert the data of the POST request into a object similar to a 
        simple JSON object.
        """
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

class StartView(LoginRequiredMixin, RedirectView):
    """ 
    Check if exists quizzes of the topic chose by the user, then get a random
    quiz and load the game session, if not redirects to main page.  
    """
    pattern_name = 'question'
    login_url = '/'
    redirect_field_name = 'next'

    def get_random_survey_from_topic(self):
        surveys = list(Survey.objects.filter(
                topic=self.request.POST.get('topic'),
                status=1))                              # Only accepted surveys
        return None if not surveys else random.choice(surveys)

    def get_game_session(self, survey):
        return GameSession.new_game_session(self.request.user, survey)

    def get_redirect_url(self, *args, **kwargs):
        survey = self.get_random_survey_from_topic()

        if not survey:
            return "/?failed=1"

        self.request.session['game_ended'] = False 
        self.request.session['questions'] = list(survey.questions.values('id'))
        self.request.session['answers'] = []
        self.request.session['game_session'] = serialize(
                'json', 
                [self.get_game_session(survey)])

        return super().get_redirect_url(*args,**kwargs)

class QuestionView(ContextMixin,View):
    """
    This view is the heart of the app, provides the quiz, and stores 
    into session data the answers of the users.
    """
    def setup(self,request, *args,**kwargs):
        """ Create the context on initialization. """
        super().setup(request,*args,**kwargs)
        self.context = self.get_context_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = self.request.session.pop('questions')
        if not questions:
            return context
        question_id = questions.pop()['id']
        self.request.session['questions'] = questions
        question = Question.objects.get(id=question_id)
        context['question'] = question
        
        return context

    def get(self,request, *args, **kwargs):
        if not self.context.get('question'):
            return redirect('end')
        return render(request,'quiz/quiz.html',self.context)

    def post(self,request, *args, **kwargs):
        if request.session['game_ended']:
            return redirect('index')

        answers = request.session.pop('answers')
        answers.append((
            request.POST.get('question_id'),
            request.POST.get('choice'),
            request.POST.get('timerVal')
        ))
        request.session['answers'] = answers
        logging.debug(request.session['answers'])
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
        context['score'] = game_session.score
        context['top5'] = GameSession.scores.top_5()
        return context
