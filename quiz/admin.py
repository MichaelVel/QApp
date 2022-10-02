from django.contrib import admin

from .models import Question, Choice, Survey

class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionInLine(admin.TabularInline):
    model = Question
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    fieldsets =  [
            (None,  {'fields': ['question_text']}),
            #('Date Information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInLine]    

class SurveyAdmin(admin.ModelAdmin):
    fieldsets = [
            (None, {'fields': ['topic', 'status', 'name']}),
    ]
    inlines = [QuestionInLine,]

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
