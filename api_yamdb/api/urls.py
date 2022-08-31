from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    register, MyTokenObtainPairView,
    UsersViewSet, ReviewViewSet
)


app_name = 'api'

router = DefaultRouter()
router.register('users', UsersViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='review'
)

urlpatterns = [
    path('', include(router.urls), name='api-root'),
    path('v1/', include(router.urls)),
    path(
        'v1/auth/token/', MyTokenObtainPairView.as_view(),
        name='token'
    ),
    path(
        'v1/auth/token/refresh/', TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path('v1/auth/signup/', register, name='register'),
]
