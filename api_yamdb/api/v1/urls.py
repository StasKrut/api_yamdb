from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import get_token, register


urlpatterns = [
    path('auth/token/', get_token, name='token'),
    path(
        'auth/token/refresh/', TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path('auth/signup/', register, name='register'),
]
