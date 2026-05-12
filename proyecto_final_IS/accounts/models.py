from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('teacher', 'Profesor'),
        ('student', 'Estudiante'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    

class Course(models.Model):

    title = models.CharField(max_length=100)

    language = models.CharField(max_length=50)

    flag = models.CharField(max_length=10)

    week = models.IntegerField(default=1)

    progress = models.IntegerField(default=0)

    student = models.ForeignKey(
        User,
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
        User,
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
        return f"{self.usuario.username} - {self.curso.title} - {self.rol_en_curso}"