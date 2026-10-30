# Put this at jewellery_project/wsgi.py ONLY if that file is missing.
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jewellery_project.settings")
application = get_wsgi_application()
