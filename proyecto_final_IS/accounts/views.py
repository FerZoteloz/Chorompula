from django.shortcuts import redirect, render, get_object_or_404

# Create your views here.
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from accounts.models import Profile, Course, UsuarioCurso, CustomUser, Alumno, Profesor, CoursePost, CourseMaterial
import json


def login_view(request):
    if request.method == "GET":
        return render(request, "accounts/index.html")

    if request.method == "POST":

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "La solicitud no tiene un formato válido."
            }, status=400)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({
                "success": False,
                "message": "Correo y contraseña son obligatorios."
            }, status=400)

        user = authenticate(
            request,
            email=email,
            password=password
        )

        if user is not None:
            login(request, user)

            return JsonResponse({
                "success": True
            })

        return JsonResponse({
            "success": False,
            "message": "Usuario o contraseña incorrectos."
        }, status=401)

    return JsonResponse({
        "success": False,
        "message": "Método no permitido."
    }, status=405)


# =============================================

@login_required
def logout_view(request):
    logout(request)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True
        })

    return redirect("/login/")


# =============================================

def signup_view(request):
    if request.method == "GET":
        return render(request, "accounts/signup.html")

    if request.method == "POST":

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "La solicitud no tiene un formato válido."
            }, status=400)

        email = data.get("email")
        password = data.get("password")
        nombre = data.get("nombre_pila")
        ap_paterno = data.get("apellido_paterno")
        ap_materno = data.get("apellido_materno")
        numero_cuenta = data.get("numero_cuenta")
        rol = data.get("role", "student")

        if not email or not password or not nombre or not ap_paterno or not ap_materno:
            return JsonResponse({
                "success": False,
                "message": "Todos los campos personales son obligatorios."
            }, status=400)

        if rol == "student" and not numero_cuenta:
            return JsonResponse({
                "success": False,
                "message": "El número de cuenta es obligatorio para estudiantes."
            }, status=400)

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({
                "success": False,
                "message": "El correo ya está registrado."
            }, status=400)

        try:
            with transaction.atomic():
                # Creamos el usuario usando el correo como identificador.
                user = CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    nombre_pila=nombre,
                    apellido_paterno=ap_paterno,
                    apellido_materno=ap_materno
                )

                # Creamos el perfil del usuario con el rol correspondiente.
                perfil = Profile.objects.create(
                    user=user,
                    role=rol
                )

                # Si el usuario se registra como estudiante, también creamos su registro de alumno.
                if rol == "student":
                    Alumno.objects.create(
                        perfil=perfil,
                        numero_cuenta=numero_cuenta
                    )

                # Dejamos este bloque listo por si después se habilita registro de profesores.
                elif rol == "teacher":
                    Profesor.objects.create(
                        perfil=perfil,
                        numero_empleado=data.get("numero_empleado"),
                        especialidad=data.get("especialidad"),
                        grado_academico=data.get("grado")
                    )

            return JsonResponse({
                "success": True
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": str(e)
            }, status=400)

    return JsonResponse({
        "success": False,
        "message": "Método no permitido."
    }, status=405)


@login_required
def dashboard_view(request):
    role = request.user.profile.role

    if role == "student":
        courses = Course.objects.filter(
            usuariocurso__usuario=request.user,
            usuariocurso__rol_en_curso="student"
        ).distinct()

    elif role == "teacher":
        courses = Course.objects.filter(
            usuariocurso__usuario=request.user,
            usuariocurso__rol_en_curso="teacher"
        ).distinct()

    else:
        courses = Course.objects.all()

    context = {
        "courses": courses
    }

    if role == "admin":
        return render(request, "admin_usuarios/lista_usuarios.html", context)

    elif role == "teacher":
        return render(request, "dashboards/teacher.html", context)

    else:
        return render(request, "dashboards/student.html", context)


@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id
    )

    role = request.user.profile.role

    es_profesor_del_curso = UsuarioCurso.objects.filter(
        usuario=request.user,
        curso=course,
        rol_en_curso="teacher"
    ).exists()

    puede_publicar = role == "admin" or es_profesor_del_curso

    if puede_publicar:
        materials = CourseMaterial.objects.filter(
            course=course
        ).order_by("-uploaded_at")

    else:
        materials = CourseMaterial.objects.filter(
            course=course,
            estado="publicado"
        ).order_by("-uploaded_at")

    if request.method == "POST":
        if not puede_publicar:
            return redirect("course_detail", course_id=course.id)

        content = request.POST.get("content", "").strip()

        if content:
            CoursePost.objects.create(
                course=course,
                author=request.user,
                content=content
            )

        return redirect("course_detail", course_id=course.id)

    posts = CoursePost.objects.filter(
        course=course
    ).order_by("-created_at")

    return render(
        request,
        "dashboards/courses/course.html",
        {
            "course": course,
            "posts": posts,
            "materials": materials,
            "puede_publicar": puede_publicar
        }
    )


@login_required
def lista_usuarios_view(request):
    profiles = Profile.objects.all()

    return render(request, "admin_usuarios/lista_usuarios.html", {
        "profiles": profiles
    })

# Ini.FS.19.05.2026
@login_required
def editar_usuario_view(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == "GET":
        return render(request, "admin_usuarios/editar_usuario.html", {
            "profile": profile
        })

    if request.method == "POST":
        nombre_pila = request.POST.get("nombre_pila")
        apellido_paterno = request.POST.get("apellido_paterno")
        apellido_materno = request.POST.get("apellido_materno")
        email = request.POST.get("email")
        role = request.POST.get("role")

        if CustomUser.objects.filter(email=email).exclude(id=profile.user.id).exists():
            return render(request, "admin_usuarios/editar_usuario.html", {
                "profile": profile,
                "error": "Ese correo ya está en uso"
            })

        profile.user.nombre_pila = nombre_pila
        profile.user.apellido_paterno = apellido_paterno
        profile.user.apellido_materno = apellido_materno
        profile.user.email = email
        profile.user.save()

        profile.role = role
        profile.save()

        return redirect("/admin-usuarios/")


# Fin.FS.19.05.2026

@login_required
def crear_curso_view(request):
    if request.user.profile.role not in ["admin", "teacher"]:
        return redirect("dashboard")

    if request.method == "GET":
        return render(request, "admin_usuarios/crear_curso.html")

    if request.method == "POST":
        title = request.POST.get("nombre")
        language = request.POST.get("idioma")
        flag = request.POST.get("flag", "📘")

        if not title or not language:
            return render(request, "dashboards/crear_curso.html", {
                "error": "El nombre y el idioma del curso son obligatorios."
            })

        curso = Course.objects.create(
            title=title,
            language=language,
            flag=flag,
            week=1,
            progress=0,
            student=request.user
        )

        if request.user.profile.role == "teacher":
            UsuarioCurso.objects.get_or_create(
                usuario=request.user,
                curso=curso,
                rol_en_curso="teacher"
            )

        return redirect("dashboard")

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


# Ini.FS.19.05.2026
@login_required
def profile_settings_view(request):
    profile = request.user.profile

    emoji_options = [
        "👤", "😀", "😎", "🤓", "🧑‍💻",
        "🐱", "🐶", "🦊", "🐼", "🐧",
        "🚀", "⭐", "🔥", "🌙", "☀️",
        "🎮", "📚", "🎧", "⚽", "🍀"
    ]

    if request.method == "POST":
        selected_emoji = request.POST.get("avatar_emoji")
        avatar_image = request.FILES.get("avatar_image")

        # Primero revisamos si subió imagen
        if avatar_image:
            if profile.avatar_image:
                profile.avatar_image.delete(save=False)

            profile.avatar_image = avatar_image
            profile.save()
            return redirect("dashboard")

        # Si no subió imagen, entonces revisamos emoji
        if selected_emoji in emoji_options:
            if profile.avatar_image:
                profile.avatar_image.delete(save=False)

            profile.avatar_image = None
            profile.avatar_emoji = selected_emoji
            profile.save()
            return redirect("dashboard")

        return redirect("profile_settings")

    return render(request, "accounts/profile_settings.html", {
        "profile": profile,
        "emoji_options": emoji_options
    })


@login_required
def settings_view(request):
    return render(request, "accounts/settings.html")
# Fin.FS.19.05.2026

@login_required
def inscribirse_codigo_view(request):
    if request.user.profile.role != "student":
        return redirect("dashboard")

    mensaje = None
    error = None
    curso = None

    if request.method == "POST":
        codigo = request.POST.get("codigo_inscripcion", "").strip().upper()

        if not codigo:
            error = "Debes ingresar un código de inscripción."
        else:
            curso = Course.objects.filter(codigo_inscripcion=codigo).first()

            if not curso:
                error = "El código ingresado no existe."
            else:
                relacion_existente = UsuarioCurso.objects.filter(
                    usuario=request.user,
                    curso=curso,
                    rol_en_curso="student"
                ).exists()

                if relacion_existente:
                    mensaje = "Ya estás inscrito en este curso."
                else:
                    UsuarioCurso.objects.create(
                        usuario=request.user,
                        curso=curso,
                        rol_en_curso="student"
                    )

                    mensaje = f"Te inscribiste correctamente al curso: {curso.title}"

    return render(request, "dashboards/inscripcion_codigo.html", {
        "mensaje": mensaje,
        "error": error,
        "curso": curso
    })

@login_required
def salir_curso_view(request, course_id):
    if request.user.profile.role != "student":
        return redirect("dashboard")

    if request.method == "POST":
        relacion = UsuarioCurso.objects.filter(
            usuario=request.user,
            curso_id=course_id,
            rol_en_curso="student"
        ).first()

        if relacion:
            relacion.delete()

    return redirect("dashboard")

@login_required
def subir_material_view(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    es_profesor = UsuarioCurso.objects.filter(
        usuario=request.user,
        curso=course,
        rol_en_curso="teacher"
    ).exists()

    if not es_profesor and request.user.profile.role != "admin":
        return redirect("dashboard")

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        file = request.FILES.get("file")
        accion = request.POST.get("accion")

        if title and file:

            estado = (
                "borrador"
                if accion == "guardar_borrador"
                else "publicado"
            )

            CourseMaterial.objects.create(
                course=course,
                uploaded_by=request.user,
                title=title,
                description=description,
                file=file,
                estado=estado
            )

            return redirect(
                "course_detail",
                course_id=course.id
            )

    return render(
        request,
        "dashboards/courses/subir_material.html",
        {
            "course": course
        }
    )

@login_required
def borradores_view(request):

    borradores = CourseMaterial.objects.filter(
        uploaded_by=request.user,
        estado="borrador"
    )

    return render(
        request,
        "dashboards/courses/borradores.html",
        {
            "borradores": borradores
        }
    )

@login_required
def editar_borrador_view(request, material_id):

    material = get_object_or_404(
        CourseMaterial,
        id=material_id,
        uploaded_by=request.user
    )

    if request.method == "GET":
        return render(
            request,
            "dashboards/courses/editar_borrador.html",
            {
                "material": material
            }
        )

    if request.method == "POST":

        material.title = request.POST.get("title")
        material.description = request.POST.get("description")

        nuevo_archivo = request.FILES.get("file")

        if nuevo_archivo:
            material.file = nuevo_archivo

        material.save()

        return redirect("mis_borradores")
    
@login_required
def publicar_borrador_view(request, material_id):

    material = get_object_or_404(
        CourseMaterial,
        id=material_id,
        uploaded_by=request.user
    )

    if request.method == "POST":

        material.estado = "publicado"
        material.save()

    return redirect("mis_borradores")

@login_required
def eliminar_borrador_view(request, material_id):

    material = get_object_or_404(
        CourseMaterial,
        id=material_id,
        uploaded_by=request.user
    )

    if request.method == "POST":

        material.file.delete(save=False)
        material.delete()

    return redirect("mis_borradores")