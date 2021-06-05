# -*- coding: utf-8 -*-
import json

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone
from recommender.models import Movie


class Command(BaseCommand):
    help = "Seeds initial data for the application."

    def __init__(self):
        self.user_class = get_user_model()

        super().__init__()

    def handle(self, *args, **options):
        self.all_apps_make_migation()
        self.migrate()
        self.create_super_user()
        self.seed_movies()

    def create_super_user(self):
        if self.user_class.objects.filter(
            email=settings.ADMIN_EMAIL,
        ).exists():
            self.stdout.write("Admin account : Already exist")
            return False

        self.user_class.objects.create_superuser(
            username=settings.ADMIN_EMAIL,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
        )

        self.stdout.write(
            "Created {} admin account.".format(settings.ADMIN_EMAIL)
        )

    def all_apps_make_migation(self):
        for app in apps.get_app_configs():
            call_command("makemigrations", app.label)
            self.stdout.write("Created {} migration.".format(app.label))

    def migrate(self):
        call_command("migrate")

    def seed_movies(self):
        """
        Seed initial data movies table
        """
        try:
            with open(
                "recommender/management/commands/movies.json"
            ) as movies_json:
                initial_movies = json.load(movies_json)
                movies = [
                    Movie(
                        **movie,
                        created_at=timezone.now(),
                        updated_at=timezone.now()
                    )
                    for movie in initial_movies
                ]
                Movie.objects.bulk_create(movies)
        except Exception as e:
            self.stdout.write(str(e))
