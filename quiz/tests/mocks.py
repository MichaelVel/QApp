from typing import Any

from django.db.models.constraints import Enum
from quiz.models import Answer, GameSession, Question, Choice, Survey
from django.utils import timezone
from django.contrib.auth.models import User

class MockFactory:
    @staticmethod
    def get_correct_choice(question: Question) -> Choice:
        return Choice.objects.filter(question=question, is_correct=True)[0]

    @staticmethod
    def get_wrong_choice(question: Question) -> Choice:
        return Choice.objects.filter(question=question, is_correct=False)[0]
    
    @staticmethod
    def test_user(n:int) -> User:
        return User.objects.create_user(username=f"userTestCase{n}", password="pass")

    @staticmethod
    def test_superuser() -> User:
        return User.objects.create_superuser(username="super", password="pass")

    @staticmethod
    def test_gamesession(user: User, survey: Survey) -> GameSession:
        return GameSession.objects.create(
                creation_date=timezone.now(),
                user = user,
                survey = survey)

    @staticmethod
    def test_answer(
            session:GameSession,
            question:Question,
            choice: Choice,
            time: int) -> Answer: 
        return Answer.objects.create(session=session,
                question=question,
                choice= choice,
                interval_time = time
                )

    @staticmethod
    def test_data(user: User, n_answers: int) -> dict[str, Any]:
        """ 
        Return data as would be parsed from POST request by CreateSurveyView.
        Notice that the user is taken from the context, so to test the data is
        necessary to pass a user saved to test-database.
        """
        data = {
            'survey': {
                'topic': 'TST',
                'user': user,
            },
        }
        for i in range(n_answers):
            question_i = {
                f'question-{i}': {
                    'question_text': 'Test1',
                    'choice-0': {
                        'choice_text': 'Choice1',
                        'is_correct': False,
                    },
                    'choice-1': {
                        'choice_text': 'Choice2',
                        'is_correct': True,
                    }
                }, 
            }
            data.update(question_i)

        return data

    # @staticmethod
    # def empty_questions(n_q: int, survey: Survey) -> list[Question]:
        # """ superseded by get_data """
        # questions: list[Question] = []

        # for i in range(1, n_q+1):
            # questions.append(
                    # Question.objects.create(
                        # question_text = f"q{i}",
                        # survey = survey,
                        # pub_date = timezone.now()))
            
        # return questions

    # @staticmethod
    # def generic_choices(question: Question, n_ans: int) -> list[Choice]:
        # """ superseded by get_data """
        # answers: list[Choice] = []

        # for _ in range(n_ans-1):
            # answers.append(Choice.objects.create(choice_text="false",
                # question=question, is_correct=False))
         
        # answers.append(Choice.objects.create(choice_text="true", 
            # question=question, is_correct=True))

        # return answers

class MockChoice(Enum):
    Wrong = 0
    Correct = 1
