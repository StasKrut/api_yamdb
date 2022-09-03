from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import get_token, register


app_name = 'reviews'

urlpatterns = [
    path('token/', get_token, name='token'),
    path(
        'token/refresh/', TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path('signup/', register, name='register'),
]
