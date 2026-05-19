from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, BaseUserManager

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
    username = None # Eliminamos el username
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

    title = models.CharField(max_length=100)

    language = models.CharField(max_length=50)

    flag = models.CharField(max_length=10)

    week = models.IntegerField(default=1)

    progress = models.IntegerField(default=0)

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

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

    def __str__(self):
        return f"{self.usuario.email} - {self.curso.title} - {self.rol_en_curso}"