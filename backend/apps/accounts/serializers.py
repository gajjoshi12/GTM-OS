from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Membership, User, Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ("id", "name", "slug", "plan", "onboarding_completed", "created_at")
        read_only_fields = ("id", "slug", "created_at")


class UserSerializer(serializers.ModelSerializer):
    workspaces = serializers.SerializerMethodField()
    current_workspace = WorkspaceSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "full_name", "current_workspace", "workspaces", "date_joined")

    def get_workspaces(self, obj):
        return WorkspaceSerializer([m.workspace for m in obj.memberships.select_related("workspace")], many=True).data


def tokens_for(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    full_name = serializers.CharField(max_length=150)
    company_name = serializers.CharField(max_length=120)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def create(self, validated):
        user = User.objects.create_user(
            email=validated["email"], password=validated["password"], full_name=validated["full_name"]
        )
        ws = Workspace.objects.create(name=validated["company_name"], owner=user)
        Membership.objects.create(workspace=ws, user=user, role=Membership.Role.OWNER)
        user.current_workspace = ws
        user.save(update_fields=["current_workspace"])
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["email"].lower(), password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        attrs["user"] = user
        return attrs
