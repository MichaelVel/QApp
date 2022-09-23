from django.urls import path

from .views import (
        IndexView,
        CreateSurveyView, 
        StartView,
        QuestionView,
        EndView,
        ResultsView
        )

urlpatterns = [
        path('', IndexView.as_view(), name='index'),
        path('quiz/start', StartView.as_view(), name='start'),
        path('quiz/play', QuestionView.as_view(), name='question'),
        path('quiz/finish', EndView.as_view(), name='end'),
        path('quiz/results', ResultsView.as_view(), name='results'),
        path('create-survey', CreateSurveyView.as_view(), name='create'),
]
