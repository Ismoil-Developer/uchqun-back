from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import (
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    GroupSerializer
)
from .models import Group


class LoginView(APIView):
    """
    Tizimga kirish (Figma 1-ekran).
    Foydalanuvchi administratsiya bergan email va parol bilan tizimga kiradi.
    Muvaffaqiyatli kirganda JWT access va refresh tokenlar hamda foydalanuvchi ma'lumotlari qaytariladi.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Auth'],
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Muvaffaqiyatli kirish"),
            400: OpenApiResponse(description="Noto'g'ri login/parol"),
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = data['user']
        user_serializer = UserSerializer(user, context={'request': request})

        return Response({
            'message': 'Tizimga muvaffaqiyatli kirildi.',
            'access': data['access'],
            'refresh': data['refresh'],
            'user': user_serializer.data,
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Foydalanuvchi profil ma'lumotlarini olish va tahrirlash (Figma Mening profilim).
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Profile'])
    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    """
    Parolni o'zgartirish.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Profile'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({"detail": "Parol muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)


class GroupListView(generics.ListAPIView):
    """
    O'quv guruhlari ro'yxati.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Profile'])
    def get_queryset(self):
        return super().get_queryset()
