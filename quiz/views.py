from django.shortcuts import render
from django.contrib.auth import authenticate, login

def index(request): 
    return render(request,'quiz/index.html')

def login_view(request): 
    username = request.POST['username']
    password = request.POST['password']
    
    user = authenticate(username=username, password=password)

    if user is not None:
        login(request,user)

    return render(request,'quiz/index.html')
    

