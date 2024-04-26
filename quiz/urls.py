from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (
        IndexView,
        QLoginView,
        CreateSurveyView,
        StartView,
        QuestionView,
        ResultsView,
        ListSurveysView,
        SurveyDetailsView,
        SurveyView,
        )

urlpatterns = [
        path('', IndexView.as_view(), name='index'),
        path('accounts/login/', QLoginView.as_view(), name='login'),
        path('accounts/logout/', LogoutView.as_view(), name='login'),
        path('quiz/start', StartView.as_view(), name='start'),
        path('quiz/<int:id>', SurveyView.as_view(), name='survey'),
        path('quiz/<int:s_id>/questions/<int:q_id>', QuestionView.as_view(), name='question'),
        path('quiz/<int:id>/results', ResultsView.as_view(), name='results'),
        path('create-survey', CreateSurveyView.as_view(), name='create'),
        path('surveys/list', ListSurveysView.as_view(), name='surveys'),
        path('surveys/list/<str:topic>/<int:pk>', 
            SurveyDetailsView.as_view(), 
            name='survey-detail'),
]
