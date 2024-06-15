import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS = (
    'discordBot_django',
)
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TIME_ZONE = 'Canada/Pacific'

USE_TZ = True

# Write a random secret key here
SECRET_KEY = '4e&6aw+(5&cg^_!05r(&7_#dghg_pdgopq(yk)xa^bog7j)^*j'
