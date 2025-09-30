import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # local apps
    "accounts",
    "catalog",
    "core",
    "orders",
    "payments",
]

AUTH_USER_MODEL = 'accounts.CustomUser'


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# (Optional) Switch to Postgres later for prod—use env vars PGDATABASE, PGUSER, PGPASSWORD, PGHOST, PGPORT.

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

LOGIN_REDIRECT_URL = 'home'          # name of home url (we add this below)
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = "webmaster@localhost"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Payments
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
# Use "usd" by default. (Some processors don’t support BDT directly.)
CURRENCY = "usd"




# --- bKash ---
BKASH = {
    "SANDBOX": True,
    # Tokenized Checkout v1.2.0-beta base (bKash docs)
    # Sandbox: https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized
    # Live:    https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized
    "BASE_URL": os.getenv("BKASH_BASE_URL", "https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized"),
    "APP_KEY": os.getenv("BKASH_APP_KEY", ""),
    "APP_SECRET": os.getenv("BKASH_APP_SECRET", ""),
    "USERNAME": os.getenv("BKASH_USERNAME", ""),
    "PASSWORD": os.getenv("BKASH_PASSWORD", ""),
}

# --- Nagad ---
NAGAD = {
    "BASE_URL": os.getenv("NAGAD_BASE_URL", "https://sandbox-ssl.mynagad.com:10061"),  # sandbox host seen in examples
    "MERCHANT_ID": os.getenv("NAGAD_MERCHANT_ID", ""),
    "PUBLIC_KEY": os.getenv("NAGAD_PUBLIC_KEY", ""),     # PEM string
    "PRIVATE_KEY": os.getenv("NAGAD_PRIVATE_KEY", ""),   # PEM string
    "CALLBACK_URL": os.getenv("NAGAD_CALLBACK_URL", "https://example.com/payments/nagad/callback/"),
}

# Where bKash should return your customer (this must be publicly reachable)
PAYMENT_RETURN_SUCCESS_URL = os.getenv("PAYMENT_SUCCESS_URL", "/payments/success/")
PAYMENT_RETURN_FAIL_URL    = os.getenv("PAYMENT_FAIL_URL", "/payments/fail/")
