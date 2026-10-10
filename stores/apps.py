from django.apps import AppConfig


class StoresConfig(AppConfig):
    name = 'stores'

    def ready(self):
        try:
            from pillow_heif import register_heif_opener
        except ImportError:
            return

        register_heif_opener()
