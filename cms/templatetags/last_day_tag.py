from django import template
from datetime import datetime
register = template.Library()


@register.filter
def ldt(date):
    return int((date - datetime(2020, 12,20).date()).days * 11.5)
