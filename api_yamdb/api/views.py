import random
import string

from rest_framework import viewsets, filters, status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import default_token_generator
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage

from .models import User
from .serializers import (
    MyTokenObtainPairSerializer,
    SendEmailSerializer,
    UsersSerializer,
)
from .permissions import (
    IsAdminOrReadOnly,
    IsOwner
)


def generate_code():
    code_letters = string.ascii_uppercase
    code = ''.join(random.choice(code_letters) for i in range(9))
    return code


class SendEmailViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SendEmailSerializer

    def perform_create(self, serializer):

        try:
            user = User.objects.create_user(
                email=self.request.data.get('email'),
                username=self.request.data.get('email').partition("@")[0],
            )
        except IntegrityError:
            User.objects.get(email=self.request.data.get('email')).delete()
            user = User.objects.create_user(
                email=self.request.data.get('email'),
                username=self.request.data.get('email').partition("@")[0],
            )
        confirmation_code = default_token_generator.make_token(user)
        user_email = user.email
        user.confirmation_code = confirmation_code
        user.password = make_password(confirmation_code)
        user.save()
        email = EmailMessage('YAMDB confirmation code: ', confirmation_code,
                             to=[user_email, ])
        email.send()


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated, IsOwner)
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)
    lookup_field = 'username'

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        allow_all = user.is_superuser or user.is_staff
        if self.action == 'list' and not allow_all:
            raise PermissionDenied('ERROR: Access denied')
        return User.objects.all()

    @action(detail=False, methods=['GET', 'PATCH'], url_path='me',
            permission_classes=(IsOwner, IsAuthenticated,))
    def get_or_update_user(self, request):
        himself = User.objects.get(username=self.request.user)
        if request.method == 'GET':
            serializer = self.get_serializer(himself)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = self.get_serializer(himself, data=request.data,
                                             partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
