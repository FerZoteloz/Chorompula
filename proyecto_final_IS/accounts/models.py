from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, BaseUserManager
import random
import string
from django.conf import settings


# Create your models here.

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Eliminamos el username
    email = models.EmailField('correo electrónico', unique=True)

    # Tenemos que hacer que coincidan con la DB propuesta originalmente
    nombre_pila = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=30)
    apellido_materno = models.CharField(max_length=30)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre_pila', 'apellido_paterno']

    objects = UsuarioManager()


class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('teacher', 'Profesor'),
        ('student', 'Estudiante'),
    )

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    # Ini.FS.19.05.2026
    avatar_emoji = models.CharField(
        max_length=10,
        blank=True,
        default="👤"
    )

    avatar_image = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.role}"


class Alumno(models.Model):
    perfil = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key=True)
    numero_cuenta = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.perfil.user.email} - {self.numero_cuenta}"


class Profesor(models.Model):
    perfil = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key=True)
    numero_empleado = models.IntegerField(unique=True)
    especialidad = models.CharField(max_length=50)
    grado_academico = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.perfil.user.email} - {self.especialidad}"


class Course(models.Model):
    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("cerrado", "Cerrado"),
    ]
    title = models.CharField(max_length=100)

    language = models.CharField(max_length=50)

    flag = models.CharField(max_length=10)

    week = models.IntegerField(default=1)

    progress = models.IntegerField(default=0)

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="activo"
    )

    codigo_inscripcion = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        null=True
    )

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    def generar_codigo(self):
        letras = self.language[:3].upper() if self.language else "CUR"
        aleatorio = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=5)
        )
        return f"{letras}-{aleatorio}"

    def save(self, *args, **kwargs):
        if not self.codigo_inscripcion:
            codigo = self.generar_codigo()

            while Course.objects.filter(codigo_inscripcion=codigo).exists():
                codigo = self.generar_codigo()

            self.codigo_inscripcion = codigo

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class UsuarioCurso(models.Model):
    ROL_CURSO_CHOICES = (
        ('teacher', 'Profesor'),
        ('student', 'Estudiante'),
    )

    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    curso = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    rol_en_curso = models.CharField(
        max_length=20,
        choices=ROL_CURSO_CHOICES
    )

    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'curso', 'rol_en_curso')

    # Fin.FS.19.05.2026
    def __str__(self):
        return f"{self.usuario.email} - {self.curso.title} - {self.rol_en_curso}"


class CoursePost(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Publicación de {self.author.email} en {self.course.title}"


class Material(models.Model):

    ESTADO_CHOICES = [
        ('borrador', '📝 Borrador'),
        ('publicado', '✅ Publicado'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="materials"
    )

    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    titulo = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    archivo = models.FileField(upload_to="materiales_cursos/")

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')

    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.titulo}"