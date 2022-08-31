from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth import views as auth_views

def index(request): 
    return render(request,'quiz/index.html')

