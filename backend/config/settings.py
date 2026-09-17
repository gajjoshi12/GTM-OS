"""
Django settings for the AI GTM OS backend.

Everything secret / environment-specific is read from the repo-root `.env`
(see `.env.example`). Blank keys are fine - the platform degrades gracefully to
simulation mode per provider.
"""
from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# Load repo-root .env first, then backend/.env (backend wins if both define a key)
load_dotenv(ROOT_DIR / ".env")
load_dotenv(BASE_DIR / ".env", override=True)

# `.env` documents "leave it blank and it is not configured", but several libraries
# test for the variable's PRESENCE rather than its truthiness and happily accept an
# empty string as a real value:
#   * dj-database-url  -> blank DATABASE_URL returns {} instead of the SQLite default
#   * groq / openai    -> blank *_BASE_URL becomes the base URL, so every call 404s
# Dropping empty vars makes "blank" genuinely mean "unset" everywhere.
for _key in [k for k, v in os.environ.items() if v == ""]:
    del os.environ[_key]


def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def env_bool(key: str, default: bool = False) -> bool:
    return env(key, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(key: str, default: str = "") -> list[str]:
    return [x.strip() for x in env(key, default).split(",") if x.strip()]


SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-insecure-secret-key-change-me")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1") + (["*"] if DEBUG else [])

# Render (and most PaaS) inject the service hostname at runtime - trust it automatically.
_RENDER_HOST = env("RENDER_EXTERNAL_HOSTNAME", "")
if _RENDER_HOST and _RENDER_HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_RENDER_HOST)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    # project
    "apps.accounts",
    "apps.core",
    "apps.agents",
    "apps.knowledge",
    "apps.leads",
    "apps.outbound",
    "apps.campaigns",
    "apps.analytics",
    "apps.integrations",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        # Serverless Postgres (Neon, Supabase) suspends idle compute and drops the
        # socket. Without this, the first request after a sleep dies on a stale
        # persistent connection instead of transparently reconnecting.
        conn_health_checks=True,
    )
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CORS -------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
CORS_ALLOW_CREDENTIALS = True

# Behind Render/Heroku/Nginx the TLS terminates at the proxy; without this Django
# thinks every request is plain HTTP and rejects admin/session POSTs as insecure.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "") + (
    [f"https://{_RENDER_HOST}"] if _RENDER_HOST else []
)
CORS_ALLOW_HEADERS = [
    "accept", "authorization", "content-type", "origin", "x-csrftoken", "x-requested-with", "x-workspace",
]

# --- DRF --------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",)
    + (("rest_framework.renderers.BrowsableAPIRenderer",) if DEBUG else ()),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(env("JWT_ACCESS_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(env("JWT_REFRESH_DAYS", "14"))),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- Celery (optional) ----------------------------------------------
REDIS_URL = env("REDIS_URL", "")
CELERY_BROKER_URL = REDIS_URL or "memory://"
CELERY_RESULT_BACKEND = REDIS_URL or "cache+memory://"
CELERY_TASK_ALWAYS_EAGER = not bool(REDIS_URL)  # no Redis -> run agent jobs inline
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TIMEZONE = TIME_ZONE

# --- Platform -----------------------------------------------------------
PUBLIC_APP_URL = env("PUBLIC_APP_URL", "http://localhost:5173")
PUBLIC_API_URL = env("PUBLIC_API_URL", "http://localhost:8000")
CREDENTIALS_ENCRYPTION_KEY = env("CREDENTIALS_ENCRYPTION_KEY", "")

# --- AI -----------------------------------------------------------------
# Which vendor the agents reason through: groq (default) | anthropic | openai
LLM_PROVIDER = env("LLM_PROVIDER", "groq").strip().lower()

# Groq (primary)
GROQ_API_KEY = env("GROQ_API_KEY", "")
GROQ_MODEL = env("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_WORKER_MODEL = env("GROQ_WORKER_MODEL", "llama-3.1-8b-instant")
GROQ_BASE_URL = env("GROQ_BASE_URL", "")            # blank = SDK default
GROQ_TEMPERATURE = float(env("GROQ_TEMPERATURE", "0.6") or 0.6)
GROQ_MAX_RETRIES = int(env("GROQ_MAX_RETRIES", "5") or 5)
GROQ_TIMEOUT = float(env("GROQ_TIMEOUT", "120") or 120)
# Only some Groq models accept reasoning_effort — off by default to avoid 400s.
GROQ_SEND_REASONING_EFFORT = env_bool("GROQ_SEND_REASONING_EFFORT", False)

# Anthropic (optional alternative)
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = env("ANTHROPIC_MODEL", "claude-opus-5")
ANTHROPIC_WORKER_MODEL = env("ANTHROPIC_WORKER_MODEL", "claude-sonnet-5")

# OpenAI / OpenAI-compatible gateway (optional alternative)
OPENAI_API_KEY = env("OPENAI_API_KEY", "")
OPENAI_MODEL = env("OPENAI_MODEL", "gpt-4.1")
OPENAI_WORKER_MODEL = env("OPENAI_WORKER_MODEL", "gpt-4.1-mini")
OPENAI_BASE_URL = env("OPENAI_BASE_URL", "")

# --- Human control defaults -------------------------------------------------
DEFAULT_CONTROL_MODE = env("DEFAULT_CONTROL_MODE", "autonomous_with_approval")
DEFAULT_DAILY_SPEND_CAP = float(env("DEFAULT_DAILY_SPEND_CAP", "200000") or 0)
DEFAULT_CURRENCY = env("DEFAULT_CURRENCY", "INR")
AI_CAN_CHANGE_PRICING = env_bool("AI_CAN_CHANGE_PRICING", False)
AI_CAN_EMAIL_UNAPPROVED_ICPS = env_bool("AI_CAN_EMAIL_UNAPPROVED_ICPS", False)
COMPLIANCE_GATE_REQUIRED = env_bool("COMPLIANCE_GATE_REQUIRED", True)
REGULATED_VERTICAL = env_bool("REGULATED_VERTICAL", False)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", "INFO")},
}
