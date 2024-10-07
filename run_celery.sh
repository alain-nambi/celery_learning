source venv/bin/activate
celery -A crudproject worker --loglevel=info -E