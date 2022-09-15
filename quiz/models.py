from django.db import models
from django.contrib.auth.models import User
from django.db.models import QuerySet, Sum

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    users = models.ManyToManyField(User, through='Answer')
    objects = models.Manager()
    
    def __str__(self):
       return self.question_text 

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField("choice is correct?")
    objects = models.Manager()

    def is_correct_answer(self):
        return self.is_correct

    def __str__(self):
        return self.choice_text


class AnswerSessionManager(models.Manager):
    def get_last_session(self, user_id: int) -> int:
        ls: int= self.filter(user=user_id).aggregate(models.Max('session'))['session__max']
        return 0 if not ls else ls
    
    def get_correct_choice(self, question: Question) -> Choice:
        return Choice.objects.filter(question=question, is_correct=True)[0]


    def score(self, user_id: int, session_id: int) -> int:
        score: QuerySet = self.filter(user__id=user_id, session=session_id)
        score = score.exclude(choice__is_correct=False)
        score = score.aggregate(score=Sum('time'))

        if score['score'] is None:
            return 0

        return score['score']

    def top5_scores(self):
        scores: QuerySet = self.exclude(choice__is_correct=False)
        scores = scores.values('user__username','session')
        scores = scores.annotate(score=Sum('time'))
        scores = scores.order_by('-score')[:5]
        return scores

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

