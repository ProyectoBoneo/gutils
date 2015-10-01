import os
import sys
import django


def load_django(django_project_root, settings_module):
    sys.path.append(django_project_root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    django.setup()