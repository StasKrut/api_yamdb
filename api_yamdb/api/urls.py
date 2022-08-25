from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    SendEmailViewSet, TokenView,
    UsersViewSet, ReviewViewSet
)


app_name = 'api'

router = DefaultRouter()
router.register('auth/email', SendEmailViewSet)
router.register('users', UsersViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='review'
)

urlpatterns = [
    path('', include(router.urls), name='api-root'),
    path('v1/', include(router.urls)),
    path(
        'v1/auth/token/', TokenView.as_view(),
        name='token'
    ),
]
