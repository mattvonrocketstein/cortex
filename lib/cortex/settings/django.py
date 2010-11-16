
DEBUG             = True
TEMPLATE_DEBUG    = DEBUG

DATABASE_ENGINE   = 'sqlite3'
DATABASE_NAME     = os.path.join(DATA_DIR,'project.db')
TIME_ZONE         = 'America/LosAngeles'
LANGUAGE_CODE     = 'en-us'
SITE_ID           = 1
USE_I18N          = False
TIME_ZONE         = 'America/Chicago'

# A list of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

# Don't forget to use absolute paths, not relative paths.
TEMPLATE_DIRS = (
   os.path.join(DATA_DIR, 'templates'),
   os.path.join(VENV_SRC_ROOT, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = ("django.core.context_processors.auth",
                               'django.core.context_processors.request',
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               )



INSTALLED_APPS = (
   'django.contrib.auth',
   'django.contrib.redirects',
   'django.contrib.contenttypes',
   'django.contrib.sessions',
   'django.contrib.sites',
   'django.contrib.flatpages',
   'django.contrib.admin',
   ) + SITE_APPS
