NIKI JEWELS - deploy-ready layout (Render)

This folder = your project ROOT (the folder that holds manage.py).

INCLUDED (new / updated)
  manage.py, jewellery_project/settings.py, jewellery_project/wsgi.py
  render.yaml, requirements.txt, .gitignore
  shop/views.py + other shop/*.py I could see, templates/, static/ (with all today's changes)

NOT INCLUDED - copy these from YOUR computer into the same places (I never received them):
  jewellery_project/__init__.py
  jewellery_project/urls.py      (add the lines from docs/SETUP_PASSWORD_AND_SETTINGS.md and docs/SETUP_BANNERS.md)
  shop/__init__.py, models.py, forms.py, roles.py, checkout.py, context_processors.py,
  shop/admin.py, apps.py, urls.py, migrations/ (the whole folder)
  If you already have manage.py or wsgi.py, either copy is fine (they are the standard ones).

DO NOT upload: .env, db.sqlite3, media/, venv/

Render environment variables to set: CLOUDINARY_URL, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
(SECRET_KEY, DEBUG and DATABASE_URL are created by render.yaml)
