from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import (
    CustomUser,
    Profile,
    Alumno,
    Profesor,
    Course,
    UsuarioCurso,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        "email",
        "nombre_pila",
        "apellido_paterno",
        "apellido_materno",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_staff",
        "is_active",
    )

    search_fields = (
        "email",
        "nombre_pila",
        "apellido_paterno",
        "apellido_materno",
    )

    ordering = (
        "email",
    )

    fieldsets = (
        (None, {
            "fields": (
                "email",
                "password",
            )
        }),
        ("Información personal", {
            "fields": (
                "nombre_pila",
                "apellido_paterno",
                "apellido_materno",
            )
        }),
        ("Permisos", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Fechas importantes", {
            "fields": (
                "last_login",
                "date_joined",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": (
                "wide",
            ),
            "fields": (
                "email",
                "nombre_pila",
                "apellido_paterno",
                "apellido_materno",
                "password1",
                "password2",
                "is_staff",
                "is_active",
            ),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
    )

    list_filter = (
        "role",
    )

    search_fields = (
        "user__email",
        "user__nombre_pila",
        "user__apellido_paterno",
    )


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = (
        "perfil",
        "numero_cuenta",
    )

    search_fields = (
        "perfil__user__email",
        "perfil__user__nombre_pila",
        "numero_cuenta",
    )


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = (
        "perfil",
        "numero_empleado",
        "especialidad",
        "grado_academico",
    )

    search_fields = (
        "perfil__user__email",
        "perfil__user__nombre_pila",
        "numero_empleado",
        "especialidad",
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "language",
        "student",
        "week",
        "progress",
    )

    search_fields = (
        "title",
        "language",
        "student__email",
    )


@admin.register(UsuarioCurso)
class UsuarioCursoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "curso",
        "rol_en_curso",
        "fecha_asignacion",
    )

    list_filter = (
        "rol_en_curso",
        "fecha_asignacion",
    )

    search_fields = (
        "usuario__email",
        "curso__title",
    )