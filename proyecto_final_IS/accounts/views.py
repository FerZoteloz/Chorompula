from django.shortcuts import render

# Create your views here.
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm

class CustomLoginView(LoginView):
    template_name = 'accounts/index.html'
    authentication_form = CustomLoginForm