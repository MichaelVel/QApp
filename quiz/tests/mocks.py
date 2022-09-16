from quiz.models import Answer, Question, Choice
from django.utils import timezone
from django.contrib.auth.models import User

class MockFactory:
    @staticmethod
    def empty_questions(n_q: int) -> list[Question]:
        questions: list[Question] = []

        for i in range(1, n_q+1):
            questions.append(Question.objects.create(question_text = f"q{i}",
                pub_date = timezone.now()))
            
        return questions

    @staticmethod
    def generic_choices(question: Question, n_ans: int) -> list[Choice]:
        answers: list[Choice] = []

        for _ in range(n_ans-1):
            answers.append(Choice.objects.create(choice_text="false",
                question=question, is_correct=False))
         
        answers.append(Choice.objects.create(choice_text="true", 
            question=question, is_correct=True))

        return answers

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
    def test_answer(session:int, question:Question,
            user: User, choice: Choice, time: int) -> Answer: 
        return Answer.sessions.create(session=session,
                question=question,
                user=user,
                choice= choice,
                pub_date = timezone.now(),
                time = time
                )
