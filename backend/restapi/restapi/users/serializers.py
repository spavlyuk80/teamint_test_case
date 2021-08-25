from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from .validators import validate_email as val_email
from .tasks import enrich_user_data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )

        user.set_password(validated_data['password'])
        user.save()

        # create profile
        profile = Profile.objects.create(user=user)
        profile.save()

        # send enrichment task
        enrich_user_data.delay(user.id)

        return user

    def validate_email(self, email):
        if not val_email(email):
            raise serializers.ValidationError(
                f"{email} is not a valid email"
                )
        return email

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
