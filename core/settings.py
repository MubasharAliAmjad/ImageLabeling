"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import dj_database_url
from decouple import config
from os import path
from django.urls import reverse_lazy
from saml2 import saml
import saml2


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$szngl!cfu^8b1qt7x4^ei9qq@0x0-t$nktk*k37#j369er$%#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ["*", "https://backend.pixelpeek.xyz/"]


# Application definition

INSTALLED_APPS = [
    'API',
    'rest_framework',
    'drf_yasg',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangosaml2',
    'corsheaders'
]

MIDDLEWARE = [    
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangosaml2.middleware.SamlSessionMiddleware'
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.joinpath("templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#      'default': {
#          'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'), conn_max_age=600, conn_health_checks=True)
}


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CSRF_COOKIE_SECURE = False
# CORS_ALLOW_HEADERS = (
#     # 'Encryption-IV',
#     # 'Encryption-Key',
#     'Content-Type',
#     'Authorization',
#     'X-Requested-With',
# )

# CORS_ALLOW_CREDENTIALS = True

# "https://c840-45-117-104-111.ngrok-free.app"
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]




# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import os
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

AUTHENTICATION_BACKENDS = [
    'djangosaml2.backends.Saml2Backend',
    'API.backends.NoPasswordAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

BASEDIR = path.dirname(path.abspath(__file__))

LOGIN_URL = '/saml2/login/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
AUTH_USER_MODEL = 'API.CustomUser'    

SAML_USE_NAME_ID_AS_USERNAME = False
SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email'
SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = '__iexact'
SAML_CREATE_UNKNOWN_USER = True 
ACS_DEFAULT_REDIRECT_URL = reverse_lazy('saml_response')
SAML_ATTRIBUTE_MAPPING = {
    # 'uid': ('username', ),
    'email': ('email', ),
}
SAML_CONFIG = {
  # full path to the xmlsec1 binary programm
  'xmlsec_binary': '/usr/bin/xmlsec1',

  # your entity id, usually your subdomain plus the url to the metadata view
  'entityid': 'https://backend.pixelpeek.xyz/',
  'attribute_mapping': {
    'email': ('uid',),
   },

  # directory with attribute mapping
#   'attribute_map_dir': path.join(BASE_DIR, 'attrmap'),
#   'attribute_converters': {
#         # Example for converting the 'email' attribute
#         'email': {
#             'class': 'djangosaml2.map_attribute.EmailAttribute',
#             'attribute': 'email',  # Replace with the actual attribute name in the SAML assertion
#         },
#   },

  # Permits to have attributes not configured in attribute-mappings
  # otherwise...without OID will be rejected
  'allow_unknown_attributes': True,

  # this block states what services we provide
  'service': {
      # we are just a lonely SP
      'sp' : {
          'name': 'Federated Django sample SP',
          'name_id_format': saml2.saml.NAMEID_FORMAT_EMAILADDRESS,

          # For Okta add signed logout requests. Enable this:
          "logout_requests_signed": True,

          'endpoints': {
              # url and binding to the assetion consumer service view
              # do not change the binding or service name
              'assertion_consumer_service': [
                  ('https://backend.pixelpeek.xyz/api/saml2/acs/',
                   saml2.BINDING_HTTP_POST),
                  ],
                  # comment
              # url and binding to the single logout service view
              # do not change the binding or service name
              'single_logout_service': [
                  # Disable next two lines for HTTP_REDIRECT for IDP's that only support HTTP_POST. Ex. Okta:
                  ('https://backend.pixelpeek.xyz/api/saml2/ls/',
                   saml2.BINDING_HTTP_REDIRECT),
                  ('https://backend.pixelpeek.xyz/api/saml2/ls/post',
                   saml2.BINDING_HTTP_POST),
                  ],
              },

          'signing_algorithm':  saml2.xmldsig.SIG_RSA_SHA256,
          'digest_algorithm':  saml2.xmldsig.DIGEST_SHA256,


           # Mandates that the identity provider MUST authenticate the
           # presenter directly rather than rely on a previous security context.
          'force_authn': False,

           # Enable AllowCreate in NameIDPolicy.
          'name_id_format_allow_create': False,

           # attributes that this project need to identify a user
          'required_attributes': ['email'],

           # attributes that may be useful to have but not required
        #   'optional_attributes': ['eduPersonAffiliation'],

          'want_response_signed': True,
          'authn_requests_signed': True,
          'logout_requests_signed': True,
          # Indicates that Authentication Responses to this SP must
          # be signed. If set to True, the SP will not consume
          # any SAML Responses that are not signed.
          'want_assertions_signed': False,

          'only_use_keys_in_metadata': True,

          # When set to true, the SP will consume unsolicited SAML
          # Responses, i.e. SAML Responses for which it has not sent
          # a respective SAML Authentication Request.
          'allow_unsolicited': True,

          # in this section the list of IdPs we talk to are defined
          # This is not mandatory! All the IdP available in the metadata will be considered instead.
          'idp': {
              # we do not need a WAYF service since there is
              # only an IdP defined here. This IdP should be
              # present in our metadata

              # the keys of this dictionary are entity ids
              'https://accounts.google.com/o/saml2?idpid=C02c2knks': {
                  'single_sign_on_service': {
                      saml2.BINDING_HTTP_REDIRECT: 'https://accounts.google.com/o/saml2/idp?idpid=C02c2knks',
                      },
                  'single_logout_service': {
                      saml2.BINDING_HTTP_REDIRECT: 'https://accounts.google.com/o/saml2/idp?idpid=C02c2knks',
                      },
                  },
              },
          },
      },

  # where the remote metadata is stored, local, remote or mdq server.
  # One metadatastore or many ...
  'metadata': {
      'local': [path.join(BASE_DIR, 'GoogleIDPMetadata.xml')]
      },
# "cert": "MIIDdDCCAlygAwIBAgIGAYwteMrDMA0GCSqGSIb3DQEBCwUAMHsxFDASBgNVBAoTC0dvb2dsZSBJbmMuMRYwFAYDVQQHEw1Nb3VudGFpbiBWaWV3MQ8wDQYDVQQDEwZHb29nbGUxGDAWBgNVBAsTD0dvb2dsZSBGb3IgV29yazELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkNhbGlmb3JuaWEwHhcNMjMxMjAzMDIxODU5WhcNMjgxMjAxMDIxODU5WjB7MRQwEgYDVQQKEwtHb29nbGUgSW5jLjEWMBQGA1UEBxMNTW91bnRhaW4gVmlldzEPMA0GA1UEAxMGR29vZ2xlMRgwFgYDVQQLEw9Hb29nbGUgRm9yIFdvcmsxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpDYWxpZm9ybmlhMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0GZg0yqZSreU9F0cZNw8905SsvjwTGZLyYZRNv96MMe+8S0N32Y1GrTtsbJnnW6x1iET4J1Yth6a4SoGXnFfnXjX7WHeqK89GO0uJtn8Ve1V2HD9nOTK82tldzYzswCS6fSqrSkcmGVvtC/KZVQVW4IHEVtN3OIIjLlYJ01X1PPgchjnfgnGWQFZcxTDYUzJ89fEvCbT1IA5XHgdA042sVeMWRmDvGeB7WgegPXePSd49qPiq/j0he7nVJeIyW9yagoU5KB9Nl6TGBtNO+KbGmuor9hAXepMHaKXBgMclJ5n5Jcz90fwfCPaz5bc8ftPjwi1F0+R7YQD1ZqXTfhzeQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQA1qSW+GF4IcQiIdc1LEj3GYG4ZUkHMtolisD4XyHFkkjSedz/EiJFFIqM55XS9uzvRw3SctIEo15/D0q2Cp5IbM6kUY5BfgWAtUrtufE3gzs8GhzHm/floFhm43GjV7hR/xsnZB0UEOFhMlS1hPZ4oYB4p5GqbC5UjhAUI0TfQzvAZO1UNnUsVRRXzOE7q3syK6V11iXxfhX51YpIaBdQrims5OM6eyRA8nsipGLspxq2scPM5PJGKmED41nBaJDEu6Orfv6ES3US2fO05wCxrbzaGvRxp3WoGHQ0jjQmtEzfD/vnDJ2gW71um4xXKiXLAYle3SyWLyYkKIfBnAhux",
  # set to 1 to output debugging information
  'debug': 1,

  # Signing
  'key_file': path.join(BASE_DIR, 'private.key'),  # private part
  'cert_file': path.join(BASE_DIR, 'public.cert'),  # public part

#   # Encryption
#   'encryption_keypairs': [{
#       'key_file': path.join(BASEDIR, 'private.key'),  # private part
#       'cert_file': path.join(BASEDIR, 'public.pem'),  # public part
#   }],

  # own metadata settings
  'contact_person': [
      {'given_name': 'Mubashar',
       'sur_name': 'Ali',
       'company': 'Samaritan Technologies',
       'email_address': 'MubasharAliAmjad@gmail.com',
       'contact_type': 'technical'},
      ],
  # you can set multilanguage information here
#   'organization': {
#       'name': [('Yaco Sistemas', 'es'), ('Yaco Systems', 'en')],
#       'display_name': [('Yaco', 'es'), ('Yaco', 'en')],
#       'url': [('http://www.yaco.es', 'es'), ('http://www.yaco.com', 'en')],
#       },
  }

SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email'
# SESSION_ENGINE = 'django.contrib.sessions.backends.file'
