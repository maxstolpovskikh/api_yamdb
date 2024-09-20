from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
