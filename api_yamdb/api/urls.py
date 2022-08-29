from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CategoryViewSet, GenreViewSet, TitleViewSet

router = SimpleRouter()
router.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
router.register(
    'ganres',
    GenreViewSet,
    basename='ganres'
)
router.register(
    'titles',
    TitleViewSet,
    basename='titles'
)

urlpatterns = [
    path('v1', include(router.urls)),
]
