from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'

    def ready(self):
        import movies.signals  # noqa
#  The # noqa at the end of the import line instructs linters to ignore this line when checking the code format
