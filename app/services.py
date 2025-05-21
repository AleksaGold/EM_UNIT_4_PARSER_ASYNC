from datetime import datetime, timedelta


def seconds_until_14_11():
    """
    Возвращает количество секунд до следующего наступления 14:11 по локальному времени.

    Если текущее время уже позже 14:11, возвращается число секунд до 14:11 следующего дня.

    Returns:
        int: Количество секунд до следующего 14:11.
    """
    now = datetime.now()
    target = now.replace(hour=14, minute=11, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    return int((target - now).total_seconds())
