from django.core.exceptions import ObjectDoesNotExist

from cms.models import Article, ArticleCategory
from files.models import FileCategory


def category(request):
    categories = FileCategory.objects.all()
    return {'categories': categories}


def legal(request):
    try:
        return {'legal': Article.objects.filter(category=ArticleCategory.objects.get(name='legal'))}
    except ObjectDoesNotExist:
        return {'legal': {}}
