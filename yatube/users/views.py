from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from posts.models import Profile

from .forms import CreationForm


def singup(request):
    if request.method == 'POST':
        form = CreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            user = form.save()
            login(request, user)
            profile = Profile()
            profile.user = user
            profile.save()
            return redirect('posts:edit')
    else:
        form = CreationForm()
    return render(request, 'users/signup.html', {'form': form})
