from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from .models import Membership, Workspace
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer, tokens_for


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response({"user": UserSerializer(user).data, **tokens_for(user)}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data["user"]
        return Response({"user": UserSerializer(user).data, **tokens_for(user)})


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        if "full_name" in request.data:
            user.full_name = request.data["full_name"]
        if "current_workspace" in request.data:
            ws = Workspace.objects.filter(id=request.data["current_workspace"], memberships__user=user).first()
            if not ws:
                return Response({"detail": "Not a member of that workspace."}, status=403)
            user.current_workspace = ws
        user.save()
        return Response(UserSerializer(user).data)


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
