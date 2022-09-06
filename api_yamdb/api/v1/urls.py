from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, CommentViewSet, GenreViewSet,
    ReviewViewSet, TitleViewSet, UsersViewSet, get_token, register
)


router = DefaultRouter()
router.register('users', UsersViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='review'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router.register(
    'categories',
    CategoryViewSet,
    basename='сategories'
)
router.register(
    'titles',
    TitleViewSet,
    basename='titles'
)
router.register(
    'genres',
    GenreViewSet,
    basename='genres'
)

auth_patterns = [
    path('token/', get_token, name='token'),
    path(
        'token/refresh/', TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path('signup/', register, name='register'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_patterns))
]
