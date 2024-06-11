from django.apps import AppConfig

import sys
import os

class TfgwebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tfgWeb'

    def ready(self):
        # Add the scripts directory to the Python path
        package_path = os.path.join(self.path, 'static/scripts')
        sys.path.insert(0, package_path)