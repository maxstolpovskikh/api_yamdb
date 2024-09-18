from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from rest_framework import viewsets

from reviews.models import Category, Genre, Title
from .mixins import ListCreateDestroyViewSet
from .filters import TitleFilter
from .serializers import (CategorySerializer, GenreSerializer, TitleSerializer,
                          GetTitleSerializer)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetTitleSerializer
        return TitleSerializer
