from .mocks import MockChoice, MockFactory, create_mock_survey
from .exceptions import PlayRoundException
from django.test import TestCase
from quiz.models import Choice, GameSession, Question, Survey

class TestSurveyCreation(TestCase):
    """ Test the Survey, Question, and Choice classes. """

    @classmethod
    def setUpTestData(cls):
        cls.user = MockFactory.test_superuser()
        cls.data = MockFactory.test_data(cls.user,3)

    def test_survey_from_form(self):
        Survey.from_form(self.data)
        self.assertEqual(
                Survey.objects.all().count(),
                1)
        pass

    def test_questions_from_form(self):
        data = Survey.from_form(self.data)
        Question.from_form(data)
        self.assertEqual(
                Question.objects.all().count(),
                3)
        pass

    def test_choices_from_form(self):
        data = Survey.from_form(self.data)
        data = Question.from_form(data)
        Choice.from_form(data)
        self.assertEqual(
                Choice.objects.all().count(),
                6)
        pass

class TestQuestionModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.survey: Survey = create_mock_survey()
        cls.questions = cls.survey.questions
        cls.questions_pk = [q.pk for q in cls.survey.questions]

    def get_question(self, pk):
        try:
            i = self.questions_pk.index(pk)
            return self.questions[i] 
        except ValueError:
            return None
        
    def test_question_model_calculate_the_question_score(self):
        answers = [(1, 1, 10), (2, 3, 10), (3, 6, 10), (4, 7, 10), (5, 6, 10)]
        expected = [10, 10, 0, 10, 0]
        scores = []
        for q_pk, ch_pk, timer in answers:
            if (q := self.get_question(q_pk)) is not None:
                scores.append(q.score(ch_pk, timer))
            else:
                scores.append(0)

        for score, expected in zip(scores, expected):
            self.assertEqual(score, expected)


