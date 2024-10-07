```bash
# -E : active tasks events
celery -A crudproject worker --loglevel=info -E
```

```bash
# -E : active tasks events
celery -A crudproject worker --beat -E
```