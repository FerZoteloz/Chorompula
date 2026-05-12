from django.shortcuts import redirect, render, get_object_or_404

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
        return render(request, "admin_usuarios/lista_usuarios.html", context)

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
        "dashboards/courses/course.html",
        {
            "course": course
        }
    )

@login_required
def lista_usuarios_view(request):
    profiles = Profile.objects.all()

    return render(request, "admin_usuarios/lista_usuarios.html", {
        "profiles": profiles
    })

@login_required
def editar_usuario_view(request, profile_id):
    profile = Profile.objects.get(id=profile_id)

    if request.method == "GET":
        return render(request, "admin_usuarios/editar_usuario.html", {
            "profile": profile
        })

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        role = request.POST.get("role")

        if User.objects.filter(username=username).exclude(id=profile.user.id).exists():
            return render(request, "admin_usuarios/editar_usuario.html", {
                "profile": profile,
                "error": "Ese nombre de usuario ya está en uso"
            })

        if User.objects.filter(email=email).exclude(id=profile.user.id).exists():
            return render(request, "admin_usuarios/editar_usuario.html", {
                "profile": profile,
                "error": "Ese correo ya está en uso"
            })

        profile.user.username = username
        profile.user.email = email
        profile.user.save()

        profile.role = role
        profile.save()

        return redirect("/admin-usuarios/")