import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):

    help = "Creates superuser if it does not exists"

    def handle(self, *args, **options):
        # create superuser if missing
        if len(User.objects.filter(is_superuser=True)) == 0:
            username = os.getenv("DJANGO_ADMIN_USER", "admin")
            email = os.getenv("DJANGO_ADMIN_EMAIL", "admin@admin.com")
            password = os.getenv("DJANGO_ADMIN_PSW", "adminadmin")
            print("Creating account for %s (%s)" % (username, email))
            admin = User.objects.create_superuser(
                email=email, username=username, password=password
            )
            admin.is_active = True
            admin.is_admin = True
            admin.save()
        else:
            print("Superuser already exists")
