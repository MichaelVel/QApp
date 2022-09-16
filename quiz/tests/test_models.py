from .mocks import MockFactory
from django.test import TestCase
from quiz.models import Answer

class TestAnswerModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.questions = MockFactory.empty_questions(3)

        for question in cls.questions:
            question.save()
            question_choices = MockFactory.generic_choices(question, 3)
            for choice in question_choices:
                choice.save()
        
        cls.user1 = MockFactory.test_user(1)
        cls.user2 = MockFactory.test_user(2)

        cls.user1.save()
        cls.user2.save()

    def test_get_last_session_when_user_has_not_played(self):
        session = Answer.sessions.get_last_session(self.user2.id)
        self.assertEqual(session,0)

    def test_get_last_session_when_user_has_played_at_least_once(self):
        n = 5
        question = self.questions[1]
        for i in range(n+1):
            answer = MockFactory.test_answer(i,
                    question,
                    self.user1,
                    MockFactory.get_correct_choice(question),
                    0)
            answer.save()

        session = Answer.sessions.get_last_session(self.user1.id)
        self.assertEqual(session,n)
        

    def test_get_score(self):
        for question in self.questions:
            answer = MockFactory.test_answer(1,
                    question,
                    self.user2,
                    MockFactory.get_correct_choice(question),
                    10)
            answer.save()

        score = Answer.sessions.score(self.user2.id,1)
        self.assertEqual(score,30)

    def test_get_top5_scores(self):
        for i in range(1,8):
            for question in self.questions:
                answer = MockFactory.test_answer(i,
                        question,
                        self.user2,
                        Answer.sessions.get_correct_choice(question),
                        i*5)
                answer.save()
        expected = [(7*5*3), (6*5*3), (5*5*3), (4*5*3), (3*5*3)]
        scores = Answer.sessions.top5_scores()
        for score, expected_score in zip(scores, expected):
            self.assertEqual(score['score'],expected_score)
