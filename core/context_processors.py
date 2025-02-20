from .models import Category

def global_context(request):
    return {
        'all_categories': Category.objects.all(),
    }