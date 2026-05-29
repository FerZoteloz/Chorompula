from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import CustomUser, Profile


class Command(BaseCommand):
    help = "Crea el superadministrador institucional inicial del sistema."

    def handle(self, *args, **options):
        email = "superadmin@sgci.local"
        password = "SuperAdmin123"

        try:
            with transaction.atomic():
                user = CustomUser.objects.filter(email=email).first()

                if user is None:
                    user = CustomUser.objects.create_user(
                        email=email,
                        password=password,
                        nombre_pila="Super",
                        apellido_paterno="Admin",
                        apellido_materno="Institucional"
                    )

                    self.stdout.write(
                        self.style.SUCCESS("Usuario superadmin creado.")
                    )

                else:
                    user.set_password(password)
                    user.nombre_pila = "Super"
                    user.apellido_paterno = "Admin"
                    user.apellido_materno = "Institucional"

                    self.stdout.write(
                        self.style.WARNING("El superadmin ya existía. Se actualizaron sus datos.")
                    )

                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()

                profile, created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        "role": "superadmin"
                    }
                )

                profile.role = "superadmin"
                profile.save()

            self.stdout.write(
                self.style.SUCCESS("Superadministrador institucional listo.")
            )
            self.stdout.write(f"Correo: {email}")
            self.stdout.write(f"Contraseña temporal: {password}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"No se pudo crear el superadmin inicial: {e}")
            )