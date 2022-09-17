from django.test import Client, RequestFactory, TestCase

from quiz.views import QuestionView

from .mocks import MockFactory

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


class TestStartView(TestCase):
    def test_user_not_logged_in(self):
        """ The user must not have access to the quiz view """
        response = self.client.post('/quiz/start')
        self.assertRedirects(response, '/?next=%2Fquiz%2Fstart')

class TestQuestionView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.view = QuestionView()
        
        questions = MockFactory.empty_questions(5)
        for question in questions:
            MockFactory.generic_choices(question,3)
        
    
    def test_game_ended(self):
        """ If the flag 'game_ended' is set, the view redirects to index """ 
        request = RequestFactory().post('/quiz/1')
        request.session = {"game_ended": True }
        response = QuestionView.as_view()(request,1)

        # It's not necessary to render the redirected url
        self.assertRedirects(response, '/',fetch_redirect_response=False)

    def test_last_question(self):
        """ 
        When there is no more answers in the survey to fetch redirects to 
        end view.
        """
        request = RequestFactory().post('/quiz/1')
        request.session = {
                "game_ended": False,
                "answers": [],
                "questions": [],
        }
        response = QuestionView.as_view()(request,1)

        # It's not necessary to render the redirected url
        self.assertRedirects(response, '/quiz/finish', fetch_redirect_response=False)

class TestEndView(TestCase):
    def test_not_answers_in_session_cache(self):
        """ 
        Redirect to index if the view is access without have complete a
        survey
        """
        response = self.client.get("/quiz/finish")
        self.assertEqual(response.status_code,404)

class TestResultsView:
    """
    Empty Class. The results view just render a template and don't have
    really logic to be testted at the moment.
    """
    pass

