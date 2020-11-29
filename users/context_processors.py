from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from cms.models import Article, ArticleCategory
from files.models import FileCategory


def category(request):
    categories = FileCategory.objects.all()
    return {'categories': categories}


def legal(request):
    try:
        return {
            'legal': Article.objects.filter(category=ArticleCategory.objects.get(name='legal'))}
    except ObjectDoesNotExist:
        return {'legal': {}}


def last_day(request):
    return {'last_day': datetime(2020, 12, 20).date()}
