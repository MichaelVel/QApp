from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from .models import Answer, Question, Choice

# Create your tests here.

class TestAnswerModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.questions: dict[str,Question] = {}
        for i in range(3):
            # Creating questions
            question = Question(question_text= f"question{i}",
                    pub_date=timezone.now())
            question.save()
            cls.questions[f"question{i}"] = question

            for i in range(2):
                choice = Choice(choice_text= f"false",
                        question=question, 
                        is_correct=False)
                choice.save()

            choice_correct = Choice(choice_text="true",
                    question=question,
                    is_correct=True)
            choice_correct.save()

        cls.user1 = User(username='userTestCase1', password="pass")
        cls.user1.save()
        cls.user2 = User(username='userTestCase2', password="pass")
        cls.user2.save()

    def test_get_last_session_when_user_has_not_played(self):
        session = Answer.sessions.get_last_session(self.user2.id)
        self.assertEqual(session,0)

    def test_get_last_session_when_user_has_played_at_least_once(self):
        n = 5
        for i in range(n+1):
            answer = Answer(session=i,
                question= self.questions["question1"],
                user= self.user1,
                pub_date=timezone.now())
            answer.save()

        session = Answer.sessions.get_last_session(self.user1.id)
        self.assertEqual(session,n)
        

    def test_get_score(self):
        pass

    def test_get_top5_scores(self):
        pass
