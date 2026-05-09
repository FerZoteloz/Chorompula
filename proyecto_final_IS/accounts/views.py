from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
import json

def login_view(request):
    
    if request.method == "GET":
        return render(request, "accounts/index.html")

    if request.method == "POST":

        data = json.loads(request.body)

        username = data.get("email")
        password = data.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            return JsonResponse({
                "success": True
            })

        return JsonResponse({
            "success": False,
            "message": "Usuario o contraseña incorrectos"
        })
    
def signup_view(request):
    if request.method == "GET":
        return render(request, "accounts/signup.html")

    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "success": False,
                "message": "El correo ya está registrado."
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return JsonResponse({
            "success": True
        })