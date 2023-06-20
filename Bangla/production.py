# import dj_database_url

from .settings import *

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(" ")

REDISCLOUD_URL = config("REDISCLOUD_URL")

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDISCLOUD_URL],
        },
    },
}

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": config("CLOUDINARY_API_KEY"),
    "API_SECRET": config("CLOUDINARY_API_SECRET"),
}

# DATABASES = {
#     'default': dj_database_url.config(
#             default=config("DATABASE_URL"),
#             conn_max_age=600,
#             conn_health_checks=True,
#     )
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'bangla.sqlite3',
    }
}

INSTALLED_APPS.remove("debug_toolbar")

EMAIL_USE_TLS = True

EMAIL_USE_SSL = False

EMAIL_HOST = "smtp.gmail.com"

EMAIL_HOST_USER = config("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
}
