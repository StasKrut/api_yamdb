from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from review.models import Category, Comment, Genre, Review, Title, User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.CharField(max_length=None, min_length=None,
                                  allow_blank=False, write_only=True)
    confirmation_code = serializers.CharField(allow_blank=False,
                                              write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False
        self.fields[self.username_field].required = False

    def validate(self, attrs):
        user = User.objects.get(email=attrs['email'])
        attrs.update({'password': user.confirmation_code})
        attrs.update({'username': user.username})

        return super(MyTokenObtainPairSerializer, self).validate(attrs)

    class Meta:
        model = User
        fields = ('confirmation_code', 'email', 'token')


class SendEmailSerializer(serializers.ModelSerializer):
   username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Username "me" is not valid')
        return value

    class Meta:
        fields = ('username', 'email')
        model = User


class UsersSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role'
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id', )
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id', )
        model = Genre
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    def validate_score(self, score):
        if score < 1 or score > 10:
            raise serializers.ValidationError('Оценка должна между 1 и 10')
        return score

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
