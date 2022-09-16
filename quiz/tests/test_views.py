from django.contrib.auth.models import User
from django.test import Client, TestCase

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
    def last_question(self ):
        pass

class TestEndView(TestCase):
    def not_answers_in_session_cache(self):
        """ 
        Redirect to index if the view is access without have complete a
        survey
        """
        pass

class TestResultsView:
    """
    Empty Class. The results view just render a template and don't have
    really logic to be testted at the moment.
    """
    pass

