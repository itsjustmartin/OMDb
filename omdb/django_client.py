from django.conf import settings

from omdb.client import OmdbClient

# This prevents manage.py from running unless the DJANGO_OMDB_KEY value is present as an environment variable. So,
#  you would either need to export this variable before running manage.py:
# OMDB_KEY = values.SecretValue()
# Since you’re only using this project and key for your own personal development, 
# choose to hard code the API key directly into the settings.py file.
def get_client_from_settings():
    """Create an instance of an OmdbClient using the OMDB_KEY from the Django settings."""
    return OmdbClient(settings.OMDB_KEY)

# Rather than integrate OmdbClient directly into our Django views, we’ll write three helper functions that contain the logic
