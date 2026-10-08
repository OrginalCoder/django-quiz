import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Admin foydalanuvchisini avtomatik yaratish yoki parolini yangilash"

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default=None)
        parser.add_argument('--email', type=str, default=None)
        parser.add_argument('--password', type=str, default=None)

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username'] or os.environ.get('DJANGO_SUPERUSER_USERNAME') or os.environ.get('ADMIN_USERNAME') or 'admin'
        email = options['email'] or os.environ.get('DJANGO_SUPERUSER_EMAIL') or os.environ.get('ADMIN_EMAIL') or 'admin@quiz.uz'
        password = options['password'] or os.environ.get('DJANGO_SUPERUSER_PASSWORD') or os.environ.get('ADMIN_PASSWORD') or 'admin123'

        user = User.objects.filter(username=username).first()
        if user:
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' paroli muvaffaqiyatli yangilandi."))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' muvaffaqiyatli yaratildi."))
