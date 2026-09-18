import django
from django.db import connection
from django.shortcuts import render


def status(request):
    """
    Step 0 check only: confirms Django is running and that the PostgreSQL
    connection configured in .env actually works. No app logic lives here —
    Step 1 replaces/extends this once outlets/users exist.
    """
    db_ok = False
    db_error = None
    db_version = None

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT version();')
            db_version = cursor.fetchone()[0]
            db_ok = True
    except Exception as exc:  # deliberately broad — this page's only job is to report the error
        db_error = str(exc)

    context = {
        'django_version': django.get_version(),
        'db_ok': db_ok,
        'db_version': db_version,
        'db_error': db_error,
        'db_name': connection.settings_dict.get('NAME'),
        'db_host': connection.settings_dict.get('HOST'),
    }
    return render(request, 'core/status.html', context)
