from django import template

from datetime import datetime

register = template.Library()

@register.filter(expects_localtime=True)
def time_since(value):
    if not value:
        return ""
    then = value.replace(tzinfo=None)
    now = datetime.now()
    dif = now - then
    years = int(dif.days / 365)
    if years:
        if years == 1:
            return "last year"
        else:
            return "{} years ago".format(years)
    months = int(dif.days / 30)
    if months:
        if months == 1:
            return "last month"
        else:
            return "{} months ago".format(months)
    days = dif.days
    if days:
        if days == 1:
            return "yesterday"
        else:
            return "{} days ago".format(days)
    hours = int(dif.seconds / 60 / 60)
    if hours:
        if hours == 1:
            return "{} hour ago".format(hours)
        else:
            return "{} hours ago".format(hours)
    minutes = int(dif.seconds / 60)
    if minutes:
        if minutes == 1:
            return "{} minute ago".format(minutes)
        else:
            return "{} minutes ago".format(minutes)
    seconds = dif.seconds
    if seconds:
        if seconds == 1:
            return "{} second ago".format(seconds)
        else:
            return "{} seconds ago".format(seconds)
    if dif.microseconds:
        return "1 second ago"
    return "time error" 