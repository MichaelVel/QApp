from django.urls import path

from . import views
from .views import IndexView, CreateSurveyView, QuestionView, ResultsView

urlpatterns = [
        path('', IndexView.as_view(), name='index'),
        path('quiz/start', views.start, name='start'),
        path('quiz/<int:question_id>/', QuestionView.as_view(), name='question'),
        path('quiz/finish', views.end, name='end'),
        path('quiz/results', ResultsView.as_view(), name='results'),
        path('create-survey', CreateSurveyView.as_view(), name='create'),
]
