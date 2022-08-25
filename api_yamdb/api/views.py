from rest_framework.filters import SearchFilter
from review.models import Category, Genre

from .mixins import ModelMixinSet
from .permissions import AdminUserOrReadOnly
from .serializers import CategorySerializer, GenreSerializer


class CategoryViewSet(ModelMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = ('slug',)


class GenreViewSet(ModelMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = ('slug',)
