from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    users = models.ManyToManyField(User, through='Answer')
    
    def __str__(self):
       return self.question_text 


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField("choice is correct?")

    def is_correct_answer(self):
        return self.is_correct


class AnswerSessionManager(models.Manager):
    def get_last_session(self, user_id):
        return self.filter(user=user_id).aggregate(models.Max('session'))['session__max']

    def score(self, user_id, session_id):
        answers = self.filter(user__id=user_id, session=session_id)
        score = 0

        for answer in answers:
            if not answer.choice or not answer.choice.is_correct_answer():
                continue
            score += answer.time

        return score

class Answer(models.Model):
    session = models.BigIntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice,
            on_delete=models.CASCADE,
            default=None,
            blank=True,
            null=True)
    pub_date = models.DateTimeField('date answered')
    time = models.IntegerField(default=0)

    sessions = AnswerSessionManager()

