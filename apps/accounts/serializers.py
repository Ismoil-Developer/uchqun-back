from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Group, StudentProfile, ParentProfile, UserRole


class GroupSerializer(serializers.ModelSerializer):
    teacher_name = serializers.ReadOnlyField(source='teacher.full_name')

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'teacher', 'teacher_name', 'telegram_group_url']


class StudentProfileSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source='group',
        write_only=True,
        required=False,
        allow_null=True
    )
    parent_name = serializers.ReadOnlyField(source='parent.full_name')

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'group', 'group_id', 'parent', 'parent_name',
            'total_points', 'completed_tasks_count', 'passed_quizzes_count',
            'attendance_rate', 'bio'
        ]


class UserSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'role', 'avatar', 'student_profile', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'role']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), email=email, password=password)
        if not user:
            raise serializers.ValidationError("E-mail yoki parol noto'g'ri kiritildi.")

        if not user.is_active:
            raise serializers.ValidationError("Ushbu hisob faolsizlantirilgan. Ma'muriyatga murojaat qiling.")

        refresh = RefreshToken.for_user(user)

        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski parol noto'g'ri.")
        return value
