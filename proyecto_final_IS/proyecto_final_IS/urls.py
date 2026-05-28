"""
URL configuration for proyecto_final_IS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import (
    login_view,
    logout_view,
    signup_view,
    dashboard_view,
    course_detail_view,
    lista_usuarios_view,
    editar_usuario_view,
    crear_curso_view,
    detalle_curso_view,
    asignar_profesor_view,
# Ini.FS.19.05.2026
    profile_settings_view,
    settings_view,
    editar_contacto_view,
    salir_curso_view,
# Fin.FS.19.05.2026
    inscribirse_codigo_view,
    subir_material_view,
    borradores_view,
    editar_borrador_view,
    publicar_borrador_view,
    eliminar_borrador_view,
    eliminar_material_view,
    cerrar_curso_view,
    explorar_cursos_view,
    inscribirse_directo_view,
)

urlpatterns = [
    path('', login_view, name='home'),
    path('admin/', admin.site.urls),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),

    path('user/', dashboard_view, name='user'),
    path('dashboard/', dashboard_view, name='dashboard'),

    path('admin-usuarios/', lista_usuarios_view, name='lista_usuarios'),
    path('admin-usuarios/editar/<int:profile_id>/', editar_usuario_view, name='editar_usuario'),

    path('admin-cursos/crear/', crear_curso_view, name='crear_curso'),
    path('admin-cursos/<int:course_id>/', detalle_curso_view, name='detalle_curso'),
    path('admin-cursos/<int:course_id>/asignar-profesor/', asignar_profesor_view, name='asignar_profesor'),
# Ini.FS.19.05.2026
    path('perfil/', profile_settings_view, name='profile_settings'),
    path('configuracion/', settings_view, name='settings'),
    path('contacto/', editar_contacto_view, name='editar_contacto'),
    path('inscribirse/', inscribirse_codigo_view, name='inscribirse_codigo'),
    path('curso/<int:course_id>/salir/', salir_curso_view, name='salir_curso'),
# Fin.FS.19.05.2026
    path(
        'course/<int:course_id>/',
        course_detail_view,
        name='course_detail'
    ),
    path("course/<int:course_id>/upload-material/", subir_material_view, name="upload_material"),
    path("mis-borradores/", borradores_view, name="mis_borradores"),
    path("borrador/<int:material_id>/editar/", editar_borrador_view, name="editar_borrador"),
    path("borrador/<int:material_id>/publicar/",publicar_borrador_view, name="publicar_borrador"),
    path("borrador/<int:material_id>/eliminar/", eliminar_borrador_view, name="eliminar_borrador"),
    path("material/<int:material_id>/eliminar/", eliminar_material_view, name="eliminar_material"),
    path("course/<int:course_id>/cerrar/", cerrar_curso_view, name="cerrar_curso"),
    path('explorar-cursos/', explorar_cursos_view, name='explorar_cursos'),
    path('curso/<int:course_id>/inscribirse-directo/', inscribirse_directo_view, name='inscribirse_directo'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
