import os
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if os.environ.get("DEBUG", "true").lower() == "false":
    # production settings
    DEBUG = False
    ALLOWED_HOSTS = ["*"]
    SECRET_KEY = os.environ["SECRET_KEY"]
    # ADMINS list should be 'Name Email, Name Email, Name Email...'
    ADMINS = [a.rsplit(" ", 1) for a in os.environ.get("ADMINS", "").split(",")]
    EMAIL_HOST = os.environ["EMAIL_HOST"]
    EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
    EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
    EMAIL_PORT = "587"
    EMAIL_USE_TLS = True
    REGISTRATION_DEFAULT_FROM_EMAIL = (
        DEFAULT_FROM_EMAIL
    ) = SERVER_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "bounce@openprecincts.org")
    RAW_FILE_S3_BUCKET = os.environ["RAW_FILE_S3_BUCKET"]

    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()])
else:
    # dev settings
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "debug-secret-key")
    ALLOWED_HOSTS = ["*"]
    INTERNAL_IPS = ["127.0.0.1"]
    DOMAIN = "http://localhost:8000"
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    RAW_FILE_S3_BUCKET = os.environ.get("RAW_FILE_S3_BUCKET", "openprecincts-dev")

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgres://openprecincts:testpassword@db:5432/openprecincts"
)
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
CONN_MAX_AGE = 60

CONTACT_SQS_QUEUE = os.environ.get("CONTACT_SQS_QUEUE", "incoming-collect-email")


# non-dynamic configuration

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "webpack_loader",
    "django_celery_results",
    "core",
    "contact",
    "files",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "sesame.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.append("silk.middleware.SilkyMiddleware")

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "sesame.backends.ModelBackend",
]

ROOT_URLCONF = "openprecincts_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "openprecincts_web.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "collected_static")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DATA_UPLOAD_MAX_MEMORY_SIZE = 262144000  # 250 MB

# third party apps
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    }
}

SESAME_MAX_AGE = 30 * 60  # 30 minutes

CELERY_RESULT_BACKEND = "django-db"
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "pyamqp://rabbitmq")
