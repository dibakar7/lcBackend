'''
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','name', 'email', 'password']
        extra_kwargs = {
            'password' : {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password' , None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
        
'''
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        """Check that the email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Remove password from validated_data to handle separately
        password = validated_data.pop('password', None)
        # Create the user instance without saving
        instance = self.Meta.model(**validated_data)

        # Set the password using the set_password method
        if password is not None:
            instance.set_password(password)
        
        # Save the user instance
        instance.save()
        return instance
