from django import forms
from django.forms import BaseModelFormSet, modelformset_factory
from .models import Choice, Question, Survey

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']
        labels = { 'choice_text': ''}

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']
        labels = { 'question_text': 'Pregunta' }

    def __init__(self, *args, **kwargs):
        self.index = kwargs.pop('n_choices',4)
        super(QuestionForm,self).__init__(*args,**kwargs)
    
    def get_prefix(self) -> str:
        return self.prefix

    def get_name(self) -> str:
        n = int(self.prefix.split('-')[1]) + 1
        return f"Pregunta {n}" 
    
    def get_choices(self) -> list[ChoiceForm]:
        return [ChoiceForm(prefix=f"{self.prefix}-choice-{i}") for i in range(self.index)]

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['topic']
        labels = {'topic': 'Escoge un tema'}

class QuestionFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(QuestionFormset, self).__init__(*args, **kwargs)
        self.queryset = Question.objects.none()

QuestionFormSet =  modelformset_factory( 
        Question,
        form=QuestionForm, 
        formset=QuestionFormset,
        extra=3,)


