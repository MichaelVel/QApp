from typing import Any
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import QuerySet, Sum
from django.views.generic.base import logging


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
    name = models.CharField(max_length=60,default="Quiz with no name")

    @property
    def n_questions(self):
        """ derived attribute of the Survey Model """
        return self.question_set.count()
    
    @property
    def questions(self) -> list['Question']:
        return self.question_set.all()
    
    @staticmethod
    def from_form(data_form) -> dict[str,Any]:
        """
        Takes a dict with the data of the form, and update it with a
        Survey object.
        """
        survey = Survey(topic = data_form['survey']['topic'],
                name = data_form['survey']['name'],
                creation_date = timezone.now(),
                user = data_form['survey']['user']
                )
        survey.save()
        data_form['survey'] = survey
        return data_form

    def __str__(self):
        return f"{self.name} STATUS: {self.status}"


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
    def from_form(data_form) -> dict[str,Any]:
        """
        Takes a dict with the data of the form and a Survey object. Creates
        the questions with this object and update the dict.
        """
        survey = data_form['survey']

        for key, val in data_form.items():
            if 'question' not in key:
                continue
            text = val.pop('question_text')
            question = Question(question_text = text, survey = survey)
            question.save()
            val.update({'question': question})

        return data_form

class Choice(models.Model):
    objects = models.Manager()

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField("choice is correct?")

    def __str__(self):
        return self.choice_text

    @staticmethod
    def from_form(data_form) -> dict[str, Any]:
        """
        Takes a dict with the data of the form and Questions objects. Create
        the Choices objects of this Questions and return the updated dict.
        """
        for key, val in data_form.items():
            if 'question' not in key:
                continue
            question = val.get('question')
            for key2, val2 in val.items():
                if 'choice' not in key2:
                    continue
                choice = Choice(
                        choice_text = val2.get('choice_text'),
                        is_correct = val2.get('is_correct'),
                        question = question)
                choice.save()
                val.update({key2:choice})

        return data_form

class GamesSessionManagerScores(models.Manager):
    def top_n_scores(self, n: int, survey: Survey):
        """ Return the top n results of the given survey """
        sessions = self.filter(survey=survey)
        scores = []
        for session in sessions:
            scores.append((session.user,session.score))
        scores = sorted(scores, key= lambda x: x[1], reverse=True)
        return scores[:n]            

class GameSession(models.Model):
    objects = models.Manager()
    scores = GamesSessionManagerScores()

    creation_date = models.DateTimeField('date of creation')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def score(self):
        """ derived attribute of the GameSession Model """
        score = self.answer_set.exclude(choice__is_correct=False)
        score = score.aggregate(score=Sum('interval_time'))
        score = score['score']
        return 0 if score is None else score

    @staticmethod
    def new_game_session(user,survey) -> 'GameSession':
        return GameSession(user=user,survey=survey, creation_date = timezone.now())


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

    @staticmethod
    def new_answer(session, question, choice, interval_time) -> 'Answer':
        return Answer(
                session=session,
                question=question,
                choice=choice,
                interval_time=interval_time)




