from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, Review


class SendEmailSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=None, min_length=None,
                                  allow_blank=False)

    class Meta:
        model = User
        fields = ('email',)


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
