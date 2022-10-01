from django.middleware.csrf import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login

from .forms import NewUserForm

def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect("/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewUserForm()
    
    logging.debug(form.errors.as_data)
    return render(request, 'registerUsers/register.html', {'form': form})

