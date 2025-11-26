import calendar

from django.utils import timezone


def select_period(year, month):
    """検索期間を返す"""
    if str(month).upper() == "ALL":
        tstart = timezone.datetime(int(year), 1, 1, 0, 0, 0)
        tend = timezone.datetime(int(year), 12, 31, 0, 0, 0)
    else:
        last_day = calendar.monthrange(int(year), int(month))[1]
        tstart = timezone.datetime(int(year), int(month), 1, 0, 0, 0)
        tend = timezone.datetime(int(year), int(month), last_day, 0, 0, 0)
    return tstart, tend
