from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'fetch-arxiv-papers-daily': {
        'task': 'app.fetch_and_process_arxiv_papers',
        'schedule': crontab(hour=0, minute=0)  # Run daily at midnight
    },
}