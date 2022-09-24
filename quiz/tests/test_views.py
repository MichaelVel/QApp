from django.test import Client, RequestFactory, TestCase

from quiz.views import CreateSurveyView, EndView, QuestionView, StartView
from quiz.models import Survey, Question, Choice

from .mocks import MockFactory, MockRequest

class TestIndexView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_user_not_logged_in(self):
        """ 
        The html response must have a link to the login view  and the 
        register view. 
        """
        response = self.client.get('/')
        self.assertContains(response, '/register')
        self.assertContains(response, 'accounts/login/')

    def test_user_is_logged_in(self):
        """ The html response must have a link to the logout view. """
        MockFactory.test_user(1)
        self.client.login(username="userTestCase1",password="pass")
        response = self.client.get('/')
        self.assertContains(response, 'accounts/logout/')

    def test_user_is_admin(self):
        """ The html response must have a link to the admin view. """
        MockFactory.test_superuser()
        self.client.login(username="super",password="pass")
        response = self.client.get('/')
        self.assertContains(response, 'admin/')

class TestCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.view = CreateSurveyView()
        cls.user = MockFactory.test_user(1)

    def test_process_request(self):
        POST_data = {
            'topic': 'TST',
            'question-0-question_text': 'TestQuestion1',
            'question-0-choice_set': 'choice-1',
            'question-0-choice-0-choice_text': 'Choice1',
            'question-0-choice-1-choice_text': 'Choice2',
        }
        expected = {
                'survey': {
                    'topic': 'TST',
                    'user': self.user,
                },
                'question-0': {
                    'question_text': 'TestQuestion1',
                    'choice-0': {
                        'choice_text': 'Choice1',
                        'is_correct': False,
                    },
                    'choice-1': {
                        'choice_text': 'Choice2',
                        'is_correct': True,
                    },
                }
        }
        request = MockRequest(self.user,POST_data)
        result = self.view.process_request(request)
        
        self.assertDictEqual(result, expected)

class TestStartView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.view = StartView()
        cls.user = MockFactory.test_user(1)

        # Populate database
        cls.surveys = []
        for _ in range(5):
            data = MockFactory.test_data(cls.user,3)
            data = Survey.from_form(data)
            data = Question.from_form(data)
            data = Choice.from_form(data)
            cls.surveys.append(data['survey'])

        # Only 3 surveys accepted by the admin
        for survey in cls.surveys[:3]:
            survey.status = Survey.StateSurvey.ACCEPTED
            survey.save()


    def test_user_not_logged_in(self):
        """ The user must not have access to the quiz view """
        response = self.client.post('/quiz/start')
        self.assertRedirects(response, '/?next=%2Fquiz%2Fstart')

    def test_only_accepted_surveys_selected(self):
        survey = self.view.get_random_survey_from_topic('TST')
        self.assertIsNotNone(survey)
        self.assertEqual(survey.status, Survey.StateSurvey.ACCEPTED)

    def test_redirects_to_main_page_when_no_surveys_of_topic(self):
        Survey.objects.all().delete()
        survey = self.view.get_random_survey_from_topic('TST')
        self.assertIsNone(survey)
        
        self.client.login(username='userTestCase1',password='pass')
        response = self.client.post('/quiz/start',{'topic':'TST'})
        self.assertRedirects(response, '/?failed=1')


class TestQuestionView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.view = QuestionView()
        
        # populate database with mock survey
        cls.user = MockFactory.test_superuser()
        cls.data = MockFactory.test_data(cls.user,3)
        cls.data = Survey.from_form(cls.data)
        cls.data = Question.from_form(cls.data)
    
    def test_game_ended(self):
        """ If the flag 'game_ended' is set, the view redirects to index """ 
        request = RequestFactory().post('/quiz')
        request.session = {'questions': None, 'answers': []}
        response = QuestionView.as_view()(request)

        # It's not necessary to render the redirected url
        self.assertRedirects(response, '/quiz/finish',fetch_redirect_response=False)


class TestEndView(TestCase):
     def test_not_answers_in_session_cache(self):
        """ 
        Redirect to index if the view is access without have complete a
        survey
        """
        request = RequestFactory().get('/quiz/finish')
        request.session = {'answers': None}
        response = EndView.as_view()(request)
        self.assertRedirects(response,'/', fetch_redirect_response=False)

class TestResultsView:
    """
    Empty Class. The results view just render a template and don't have
    really logic to be tested at the moment.
    """
    pass

