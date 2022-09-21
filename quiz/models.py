from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import QuerySet, Sum


class Survey(models.Model):
    objects = models.Manager()

    class StateSurvey(models.IntegerChoices):
        REVIEW = 0, 'Pending of review'
        ACCEPTED = 1, 'Accepted by the admin'

    class SurveyTopics(models.TextChoices):
        TEST = 'TST', 'Test Survey'
        WETLANDS = 'HUM', 'Humedales'
        PARAMO = 'PAR', 'Páramo'
        CLOUD_FOREST = 'CLO', 'Bosque de niebla'
        RAIFOREST = 'RAI', 'Bosque Humedo'
        DRYFOREST = 'DRY', 'Bosque Seco'
        INSULAR = 'ISL', 'Ecosistemas Insulares'
        MANGROVE = 'MGV', 'Manglares'
        CORAL_REEF = 'COR', 'Arrecifes de Coral'

    topic = models.CharField(
            max_length=15,
            choices =  SurveyTopics.choices,
            default = SurveyTopics.TEST
    )
    status = models.SmallIntegerField(
            choices=StateSurvey.choices,
            default=StateSurvey.REVIEW
    )
    creation_date = models.DateTimeField('date of creation')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def n_questions(self):
        """ derived attribute of the Survey Model """
        return self.question_set.count()

    def __str__(self):
        return f"Survey of {self.user} in {self.topic}. STATUS: {self.status}"
    
    @staticmethod
    def from_form(request, survey_from_form: 'Survey') -> 'Survey':
        survey_from_form.user = request.user
        survey_from_form.status = Survey.StateSurvey.REVIEW
        survey_from_form.creation_date = timezone.now()
        return survey_from_form



class Question(models.Model):
    objects = models.Manager()

    question_text = models.CharField(max_length=200)
    survey = models.ForeignKey(Survey, on_delete= models.CASCADE)
    
    @property
    def correct_answer(self):
        """ derived attribute of the Question Model """
        return self.choice_set.filter(is_correct=True)

    def __str__(self):
       return self.question_text 

    @staticmethod
    def questions_from_form(request) -> list['Question']:
        questions = []
        for q in request.POST:
            if 'question_text' not in q:
                continue
            question = Question()
            question.question_text = request.POST[q]
            questions.append(question)

        return questions

class Choice(models.Model):
    objects = models.Manager()

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField("choice is correct?")

    def __str__(self):
        return self.choice_text

    @staticmethod
    def choices_from_form(request) -> list['Choice']:
        choices = []
        for ch in request.POST:
            if 'choice_text' not in ch:
                continue
            choice = Choice()
            choice.choice_text = request.POST[ch]
            choice.is_correct = False 
            choices.append(choice)

        return choices

class GameSession(models.Model):
    objects = models.Manager()

    creation_date = models.DateTimeField('date of creation')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def score(self):
        """ derived attribute of the GameSession Model """
        score = self.answer_set.exclude(choice__is_correct=False)
        score = score.aggergate(score=Sum('interval_time'))
        score = score['score']
        return 0 if score is None else score


## All what did this custom manager is now managed by the SessionGame Model. 
# class AnswerSessionManager(models.Manager):
    # def get_last_session(self, user_id: int) -> int:
        # ls: int= self.filter(user=user_id).aggregate(models.Max('session'))['session__max']
        # return 0 if not ls else ls

    # def score(self, user_id: int, session_id: int) -> int:
        # score: QuerySet = self.filter(user__id=user_id, session=session_id)
        # score = score.exclude(choice__is_correct=False)
        # score = score.aggregate(score=Sum('time'))

        # if score['score'] is None:
            # return 0

        # return score['score']

    # def top5_scores(self):
        # scores: QuerySet = self.exclude(choice__is_correct=False)
        # scores = scores.values('user__username','session')
        # scores = scores.annotate(score=Sum('time'))
        # scores = scores.order_by('-score')[:5]
        # return scores

class Answer(models.Model):
    objects = models.Manager()
    #sessions = AnswerSessionManager()

    session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(
            Choice,
            on_delete=models.CASCADE,
            default=None,
            blank=True,
            null=True)
    interval_time = models.IntegerField(default=0)


