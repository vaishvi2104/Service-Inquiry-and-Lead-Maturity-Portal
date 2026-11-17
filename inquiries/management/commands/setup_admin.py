import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Idempotently initializes administrative superuser from environment variables without hardcoded secrets."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('ADMIN_USERNAME')
        email = os.environ.get('ADMIN_EMAIL', 'admin@startupsahay.com')
        password = os.environ.get('ADMIN_PASSWORD')

        if not username:
            self.stdout.write(
                self.style.NOTICE("ADMIN_USERNAME environment variable not set. Skipping admin creation.")
            )
            return

        user = User.objects.filter(username=username).first()

        if user:
            # User already exists: DO NOT reset existing password during deployment
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            if email and not user.email:
                user.email = email
            user.save(update_fields=['is_staff', 'is_superuser', 'is_active', 'email'])
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' already exists. Staff permissions verified. Password preserved.")
            )
        else:
            # New user creation: requires explicit password from environment
            if not password:
                self.stdout.write(
                    self.style.WARNING(
                        f"ADMIN_PASSWORD environment variable not set. Cannot create new superuser '{username}'."
                    )
                )
                return

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=True,
                is_active=True,
                first_name='Lead',
                last_name='Manager',
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
