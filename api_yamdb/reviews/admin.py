from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Category, Genre, Review, Title

User = get_user_model()


class TitleAdmin(admin.ModelAdmin):
    """Админка для модели Title."""
    list_display = (
        "name",
        "description",
    )
    search_fields = ("name",)
    list_filter = ("year",)


# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review)
