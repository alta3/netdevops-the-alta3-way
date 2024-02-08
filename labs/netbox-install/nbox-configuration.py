ALLOWED_HOSTS = ['*']         ############## UPDATE allowed_hosts to be any 
---
# PostgreSQL database configuration. See the Django documentation for a complete list of available parameters:
#   https://docs.djangoproject.com/en/stable/ref/settings/#databases
DATABASE = {
    'ENGINE': 'django.db.backends.postgresql',  # Database engine
    'NAME': 'netbox',         ############## UPDATE Database name
    'USER': 'netbox',         ############## UPDATE PostgreSQL username
    'PASSWORD': 'alta3',      ############## PostgreSQL password
    'HOST': 'localhost',      # Database server
    'PORT': '',               # Database port (leave blank for default)
    'CONN_MAX_AGE': 300,      # Max database connection age
}
---
SECRET_KEY = ''              ############## UPDATE with key you made in previous step
