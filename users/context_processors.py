from files.models import FileCategory


def category(request):
    categories = FileCategory.objects.all()
    return {'categories': categories}
