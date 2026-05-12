from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.models import Profile, Course
import json

def login_view(request):
    
    if request.method == "GET":
        return render(request, "accounts/index.html")

    if request.method == "POST":

        data = json.loads(request.body)

        email = data.get("email")
        password = data.get("password")

        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

            if user is not None:

                login(request, user)

                return JsonResponse({
                    "success": True
                })

        except User.DoesNotExist:
            pass

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

        Profile.objects.create(
            user=user,
            role="student"
        )

        login(request, user)

        return JsonResponse({
            "success": True
        })
    
@login_required
def dashboard_view(request):

    role = request.user.profile.role

    courses = Course.objects.filter(
        student=request.user
    )

    context = {
        "courses": courses
    }

    role = request.user.profile.role

    if role == "admin":
        return render(request, "dashboards/admin.html", context)

    elif role == "teacher":
        return render(request, "dashboards/teacher.html", context)

    else:
        return render(
            request,
            "dashboards/student.html",
            context
        )
    

@login_required
def course_detail_view(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    return render(
        request,
        "courses/detail.html",
        {
            "course": course
        }
    )