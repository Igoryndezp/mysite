import datetime


def year(request):
    now = datetime.datetime.now()
    a = now.year
    """Добавляет переменную с текущим годом."""
    return {
        'year': a,
    }
