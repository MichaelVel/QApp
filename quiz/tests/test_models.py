from .mocks import MockChoice, MockFactory
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

class TestGameSessionModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        # populate database with mock survey
        cls.user = MockFactory.test_superuser()
        cls.data = MockFactory.test_data(cls.user,3)
        cls.data = Survey.from_form(cls.data)
        cls.data = Question.from_form(cls.data)
        cls.data = Choice.from_form(cls.data)
    
    def play_round(
            self,
            game_session: GameSession,
            survey: Survey,
            user_choices: list[tuple[MockChoice,int]]) -> None:
        """
        takes a list: [(Wrong, 10),(Correct, 5),(Wrong,0),] and populate 
        the database with the session and answers data.
        """
        if survey.n_questions != len(user_choices):
            message = f"n of questions({survey.n_questions}) \
                    != len user_choices ({len(user_choices)})"
            raise PlayRoundException(message)

        questions = survey.questions
        for question, user_data in zip(questions,user_choices):
            choice = MockFactory.get_wrong_choice(question)
            if user_data[0] == MockChoice.Correct:
                choice = MockFactory.get_correct_choice(question)

            MockFactory.test_answer(game_session,question,choice,user_data[1])
        

    def test_score_return_right_answer_when_choice_is_correct(self):
        survey = self.data["survey"]
        game_session = MockFactory.test_gamesession(self.user,survey)
        user_choices = [(MockChoice.Correct,10) for _ in range(survey.n_questions)]

        self.play_round(game_session,survey,user_choices)
        self.assertEqual(game_session.score, 30)

    def test_score_return_zero_when_all_choices_are_wrong(self):
        survey = self.data["survey"]
        game_session = MockFactory.test_gamesession(self.user,survey)
        user_choices = [(MockChoice.Wrong,10) for _ in range(survey.n_questions)]

        self.play_round(game_session,survey,user_choices)
        self.assertEqual(game_session.score, 0)

    def test_get_top_n_scores_return_the_correct_n_results(self):
        survey = self.data["survey"]

        for i in range(10):
            game_session = MockFactory.test_gamesession(self.user,survey)
            user_choices = [(MockChoice.Correct,i) for _ in range(survey.n_questions)]
            self.play_round(game_session,survey,user_choices)

        expected_results = [27, 24, 21, 18, 15, 12, 9, 6, 3, 0]
        top_5_results = GameSession.scores.top_n_scores(5,survey)
        top_5_results = list(map(lambda x: x[1], top_5_results))
        self.assertEqual(expected_results[:5], top_5_results)


## Due the changes in the models these test now are obsolete. Now main logic of
## the app is in GameSession, and there is now much to test on the Answer Model
# class TestAnswerModel(TestCase):
    # @classmethod
    # def setUpTestData(cls):
        # cls.questions = MockFactory.empty_questions(3)

        # for question in cls.questions:
            # MockFactory.generic_choices(question, 3)
        
        # cls.user1 = MockFactory.test_user(1)
        # cls.user2 = MockFactory.test_user(2)


    # def test_get_last_session_when_user_has_not_played(self):
        # session = Answer.sessions.get_last_session(self.user2.id)
        # self.assertEqual(session,0)

    # def test_get_last_session_when_user_has_played_at_least_once(self):
        # n = 5
        # question = self.questions[1]
        # for i in range(n+1):
            # MockFactory.test_answer(i,
                # question,
                # self.user1,
                # MockFactory.get_correct_choice(question),
                # 0)

        # session = Answer.sessions.get_last_session(self.user1.id)
        # self.assertEqual(session,n)
        

    # def test_score_return_right_answer_when_choice_is_correct(self):
        # for question in self.questions:
            # MockFactory.test_answer(1,
                # question,
                # self.user2,
                # MockFactory.get_correct_choice(question),
                # 10)

        # score = Answer.sessions.score(self.user2.id,1)
        # self.assertEqual(score,30)

    # def test_score_return_zero_when_all_choices_are_wrong(self):
        # for question in self.questions:
            # MockFactory.test_answer(1,
                # question,
                # self.user2,
                # MockFactory.get_wrong_choice(question),
                # 10)

        # score = Answer.sessions.score(self.user2.id,1)
        # self.assertEqual(score,0)

    # def test_get_top5_scores(self):
        # for i in range(1,8):
            # for question in self.questions:
                # MockFactory.test_answer(i,
                    # question,
                    # self.user2,
                    # MockFactory.get_correct_choice(question),
                    # i*5)

        # expected = [(7*5*3), (6*5*3), (5*5*3), (4*5*3), (3*5*3)]
        # scores = Answer.sessions.top5_scores()
        # for score, expected_score in zip(scores, expected):
            # self.assertEqual(score['score'],expected_score)
