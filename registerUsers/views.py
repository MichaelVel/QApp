from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import NewUserForm

def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return redirect("/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewUserForm()

    return render(request, 'registerUsers/register.html', {'form': form})

