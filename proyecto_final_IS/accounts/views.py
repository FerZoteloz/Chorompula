from django.shortcuts import redirect, render, get_object_or_404

# Create your views here.
from django.contrib.auth import authenticate, login
#from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from accounts.models import Profile, Course, UsuarioCurso, CustomUser, Alumno, Profesor
import json

def login_view(request):
    
    if request.method == "GET":
        return render(request, "accounts/index.html")

    if request.method == "POST":

        data = json.loads(request.body)

        email = data.get("email")
        password = data.get("password")

        user = authenticate(request, email=email, password=password)

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

        nombre = data.get("nombre_pila")
        ap_paterno = data.get("apellido_paterno")
        ap_materno = data.get("apellido_materno")
        rol = data.get("role", "student") # Usamos rol por defecto
        

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({
                "success": False,
                "message": "El correo ya está registrado."
            })
        
        try:
            with transaction.atomic():
                # Creamos el usuario ya usando la separación de su nombre
                user = CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    nombre_pila=nombre,
                    apellido_paterno=ap_paterno,
                    apellido_materno=ap_materno
                )

                #Creamos el perfil del usuario con el rol correspondiente
                perfil = Profile.objects.create(user=user, role=rol)

                # Lo integramos a las tablas hijas
                # Cambie student por estudiante y teacher por profesor 
                # para que coincida con el rol
                if rol == "student":
                    Alumno.objects.create(
                        perfil=perfil,
                        numero_cuenta=data.get("numero_cuenta")
                    )
                elif rol == "teacher":
                    Profesor.objects.create(
                        perfil=perfil,
                        numero_empleado=data.get("numero_empleado"),
                        especialidad=data.get("especialidad"),
                        grado_academico=data.get("grado")
                    )

            login(request, user)
            return JsonResponse({"success": True})
            
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

"""

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

"""
    
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
    

@login_required
def crear_curso_view(request):
    if request.user.profile.role != "admin":
        return redirect("/dashboard/")

    if request.method == "GET":
        return render(request, "dashboards/crear_curso.html")

    if request.method == "POST":
        title = request.POST.get("nombre")
        language = request.POST.get("idioma")
        description = request.POST.get("descripcion")
        status = request.POST.get("estado")

        Course.objects.create(
            title=title,
            language=language,
            description=description,
            status=status,
            creator=request.user,
            flag="📘"
        )

        return redirect("/dashboard/")


@login_required
def detalle_curso_view(request, course_id):
    if request.user.profile.role != "admin":
        return redirect("/dashboard/")

    curso = get_object_or_404(Course, id=course_id)

    profesores = UsuarioCurso.objects.filter(
        curso=curso,
        rol_en_curso="teacher"
    )

    estudiantes = UsuarioCurso.objects.filter(
        curso=curso,
        rol_en_curso="student"
    )

    return render(request, "admin_usuarios/detalle_curso.html", {
        "curso": curso,
        "profesores": profesores,
        "estudiantes": estudiantes
    })


@login_required
def asignar_profesor_view(request, course_id):
    if request.user.profile.role != "admin":
        return redirect("/dashboard/")

    curso = get_object_or_404(Course, id=course_id)

    profesores_disponibles = User.objects.filter(
        profile__role="teacher"
    ).exclude(
        usuariocurso__curso=curso,
        usuariocurso__rol_en_curso="teacher"
    )

    if request.method == "GET":
        return render(request, "admin_usuarios/asignar_profesor.html", {
            "curso": curso,
            "profesores": profesores_disponibles
        })

    if request.method == "POST":
        profesor_id = request.POST.get("profesor_id")
        profesor = get_object_or_404(User, id=profesor_id)

        UsuarioCurso.objects.get_or_create(
            usuario=profesor,
            curso=curso,
            rol_en_curso="teacher"
        )

        return redirect(f"/admin-cursos/{curso.id}/")