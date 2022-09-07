from django.urls import path

from . import views
from .views import QuestionView

urlpatterns = [
        path('', views.index, name='index'),
        path('quiz/start', views.start, name='start'),
        path('quiz/<int:question_id>/', QuestionView.as_view(), name='question'),
        path('quiz/finish', views.end, name='end'),
        path('results', views.results, name='results'),
]
