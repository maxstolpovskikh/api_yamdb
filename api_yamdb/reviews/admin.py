from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Category, Genre, GenreTitle, Review, Title, User


User = get_user_model()

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(GenreTitle)
admin.site.register(Review)
