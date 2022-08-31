import random
import string

from api.filters import TitleFilter
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from review.models import Category, Genre, Review, Title, User

from .mixins import ModelMixinSet
from .permissions import (AdminModeratorAuthorPermission, IsAdminOrReadOnly,
                          IsAdminUserOrReadOnly, IsAuthorOrReadOnly, IsOwner)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, TokenSerializer,
                          ReviewSerializer, SendEmailSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UsersSerializer)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = SendEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='YaMDb registration',
        message=f'Yamdb код подтверждения: {confirmation_code}',
        from_email=None,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )

    if default_token_generator.check_token(
        user, serializer.validated_data['confirmation_code']
    ):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class CategoryViewSet(ModelMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    """
    Получить список всех жанров. Права доступа: Доступно без токена
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    """
    Получить список всех объектов. Права доступа: Доступно без токена
    """
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        new_queryset = Review.objects.filter(title=title_id)
        return new_queryset

    def perform_create(self, serializer):
        author = self.request.user
        text = self.request.data.get('text')
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        reviews = Review.objects.filter(author=author, title=title)
        if reviews.count() > 0:
            return True
        serializer.save(title=title, author=author, text=text)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        not_create_success = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if not_create_success:
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST,
                headers=headers
            )
        else:
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
