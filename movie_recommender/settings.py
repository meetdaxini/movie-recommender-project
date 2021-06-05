# Import the original settings from each template
import os

# Pulling django-environ settings file, stored in Secret Manager
import environ

from .basesettings import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(BASE_DIR, ".env")

SETTINGS_NAME = "application_settings"

if not os.path.isfile(".env"):
    import google.auth
    from google.cloud import secretmanager_v1beta1 as sm

    _, project = google.auth.default()

    if project:
        client = sm.SecretManagerServiceClient()
        path = client.secret_version_path(project, SETTINGS_NAME, "latest")
        payload = client.access_secret_version(path).payload.data.decode(
            "UTF-8"
        )

        with open(env_file, "w") as f:
            f.write(payload)

env = environ.Env(DEBUG=(bool, False), LOCAL=(bool, False))
env.read_env(env_file)

# ADMIN CONFIG
ADMIN_USERNAME = env("ADMIN_USERNAME")
ADMIN_EMAIL = env("ADMIN_EMAIL")
ADMIN_PASSWORD = env("ADMIN_PASSWORD")

# external api keys for recommensation
TASTE_API = env("TASTE_API")
TMDB_API = env("TMDB_API")
OMDB_API = env("OMDB_API")

# Setting this value from django-environ
SECRET_KEY = env("SECRET_KEY")

# Could be more explicitly set (see "Improvements")
ALLOWED_HOSTS += [env("ALLOWED_HOSTS")]

# Default false. True allows default landing pages to be visible
DEBUG = env("DEBUG")


INSTALLED_APPS += ["storages"]  # for django-storages
if "movie_recommender" not in INSTALLED_APPS:
    INSTALLED_APPS += ["movie_recommender"]  # for custom data migration


if not env("LOCAL"):
    # Setting this value from django-environ
    DATABASES = {"default": env.db()}

    # Define static storage via django-storages[google]
    GS_BUCKET_NAME = env("GS_BUCKET_NAME")
    STATICFILES_DIRS = []
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_DEFAULT_ACL = "publicRead"
