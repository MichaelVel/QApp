from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

def index(request): 
    return render(request,'quiz/index.html')

def login_view(request): 
    user = authenticate(username=request.POST['username'],
                        password=request.POST['password'])
    if user is not None:
        login(request,user)
    return redirect(index)

def logout_view(request):
    logout(request)
    return redirect(index)


