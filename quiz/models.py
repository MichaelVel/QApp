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
        return [q for q in self.question_set.all().order_by('id')]

    def next_question(self, q_id: int | None = None) -> 'Question | None':
        questions = self.questions
        if q_id is None:
            return questions[0]

        q_indexes = [q.id for q in questions]
        idx = q_indexes.index(q_id)

        if idx+1 >= len(q_indexes):
            return None

        return questions[idx+1]

    
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
        return self.choice_set.filter(is_correct=True).first()

    def score(self, choice_pk: int, timer: int):
        correct_answer = self.correct_answer
        if correct_answer is None or correct_answer.pk == choice_pk:
            return timer
        return 0

    def __str__(self):
       return f"{self.question_text}"

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
    choice_text = models.CharField(max_length=20)
    explanation = models.CharField(max_length=200, blank=True)
    is_correct = models.BooleanField("choice is correct?")

    def __str__(self):
        return f"{self.choice_text}"

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

class Answer(models.Model):
    objects = models.Manager()

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)

    @staticmethod
    def top_n_answers(n: int, survey: Survey):
        return Answer.objects.filter(survey=survey).order_by('-score')[:n]



