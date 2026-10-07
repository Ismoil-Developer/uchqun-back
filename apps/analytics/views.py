from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import F
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import Attendance, AttendanceStatus, AchievementBadge
from .serializers import AttendanceSerializer, LeaderboardEntrySerializer
from apps.accounts.models import User, StudentProfile, UserRole, Group
from apps.courses.models import CourseEnrollment, Module, Topic, TopicProgress, TopicStatus
from apps.assignments.models import AssignmentSubmission
from apps.quizzes.models import QuizAttempt


class GroupLeaderboardView(APIView):
    """
    Guruh bo'yicha umumiy reyting (Figma Reyting bo'limi).
    O'quvchilar va ota-onalar guruhdagi barcha o'quvchilarning to'plagan ballari va o'rnini ko'ra oladi.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Leaderboard & Analytics'],
        parameters=[
            OpenApiParameter(name='group_id', type=int, location=OpenApiParameter.QUERY, description="Guruh ID (agar berilmasa joriy guruh olinadi)")
        ],
        responses={200: OpenApiResponse(description="Guruh reyting jadvali")}
    )
    def get(self, request):
        user = request.user
        group_id = request.query_params.get('group_id')

        # Agar group_id berilmagan bo'lsa o'quvchining o'z guruhi olinadi
        if not group_id and hasattr(user, 'student_profile') and user.student_profile.group:
            target_group = user.student_profile.group
        elif group_id:
            target_group = get_object_or_404(Group, id=group_id)
        else:
            target_group = Group.objects.first()

        if not target_group:
            return Response({'group_name': None, 'rankings': []})

        students_profiles = StudentProfile.objects.filter(
            group=target_group
        ).select_related('user').order_by('-total_points', '-attendance_rate', 'user__first_name')

        rankings = []
        for index, sp in enumerate(students_profiles, start=1):
            u = sp.user
            avatar_url = request.build_absolute_uri(u.avatar.url) if u.avatar else None
            rankings.append({
                'rank': index,
                'student_id': u.id,
                'full_name': u.full_name,
                'email': u.email,
                'avatar': avatar_url,
                'group_name': target_group.name,
                'total_points': sp.total_points,
                'attendance_rate': float(sp.attendance_rate),
                'completed_tasks_count': sp.completed_tasks_count,
                'passed_quizzes_count': sp.passed_quizzes_count,
                'is_current_user': (u.id == user.id)
            })

        return Response({
            'group_id': target_group.id,
            'group_name': target_group.name,
            'teacher_name': target_group.teacher.full_name if target_group.teacher else None,
            'total_students': len(rankings),
            'rankings': rankings
        })


class MyAttendanceView(generics.ListAPIView):
    """
    O'quvchining o'z davomati tarixi va ko'rsatkichlari.
    """
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Leaderboard & Analytics'])
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Attendance.objects.none()
        return Attendance.objects.filter(student=self.request.user).order_by('-date')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total_records = queryset.count()
        present_count = queryset.filter(status=AttendanceStatus.PRESENT).count()
        absent_count = queryset.filter(status=AttendanceStatus.ABSENT).count()
        late_count = queryset.filter(status=AttendanceStatus.LATE).count()

        rate = round((present_count / total_records * 100), 1) if total_records > 0 else 100.0

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'attendance_rate': rate,
            'total_days': total_records,
            'present_days': present_count,
            'absent_days': absent_count,
            'late_days': late_count,
            'history': serializer.data
        })


class ParentChildrenListView(APIView):
    """
    Ota-onaga biriktirilgan farzandlar ro'yxati.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Parent Monitoring'],
        responses={200: OpenApiResponse(description="Farzandlar ro'yxati")}
    )
    def get(self, request):
        # Ota-ona yoki admin
        children_profiles = StudentProfile.objects.filter(parent=request.user).select_related('user', 'group')
        children = []
        for cp in children_profiles:
            u = cp.user
            avatar_url = request.build_absolute_uri(u.avatar.url) if u.avatar else None
            children.append({
                'student_id': u.id,
                'full_name': u.full_name,
                'email': u.email,
                'phone_number': u.phone_number,
                'avatar': avatar_url,
                'group_name': cp.group.name if cp.group else "Guruhsiz",
                'total_points': cp.total_points,
                'attendance_rate': float(cp.attendance_rate),
                'completed_tasks_count': cp.completed_tasks_count,
            })
        return Response({'children': children})


class ParentChildDashboardView(APIView):
    """
    Ota-onalar uchun farzandini to'liq nazorat qilish paneli (monitoring).
    - Guruhdagi o'rni (reyting)
    - Davomat va kelmagan kunlari
    - Qolib ketgan darslar va prezentatsiyalar (.pdf)
    - Uy vazifalari (baho, taqriz, topshirilmaganlar)
    - Test natijalari
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Parent Monitoring'],
        responses={200: OpenApiResponse(description="Farzand monitoring ma'lumotlari")}
    )
    def get(self, request, student_id):
        student = get_object_or_404(User, id=student_id, role=UserRole.STUDENT)

        # Ota-ona ruxsatini tekshirish
        if not (request.user.role == UserRole.ADMIN or request.user.is_staff):
            if hasattr(student, 'student_profile') and student.student_profile.parent != request.user:
                return Response({'detail': "Sizda ushbu o'quvchi ma'lumotlarini ko'rish huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)

        profile = getattr(student, 'student_profile', None)
        group = profile.group if profile else None

        # Guruhdagi o'rnini hisoblash
        group_rank = "-"
        total_in_group = 0
        if group:
            peers = StudentProfile.objects.filter(group=group).order_by('-total_points', '-attendance_rate')
            total_in_group = peers.count()
            for idx, p in enumerate(peers, start=1):
                if p.user_id == student.id:
                    group_rank = f"{idx}-o'rin ({total_in_group} o'quvchi orasida)"
                    break

        # Davomat hisoboti
        attendances = Attendance.objects.filter(student=student).order_by('-date')
        absent_records = attendances.filter(status=AttendanceStatus.ABSENT).values('date', 'teacher_note')

        # Qolib ketgan darslar (student yozilgan ochiq kurslarning tugallanmagan mavzulari)
        missed_topics = []
        active_course_ids = CourseEnrollment.objects.filter(
            student=student,
            status=EnrollmentStatus.OPEN
        ).values_list('course_id', flat=True)

        if active_course_ids:
            all_topics = Topic.objects.filter(module__course_id__in=active_course_ids)
            completed_topic_ids = TopicProgress.objects.filter(
                student=student,
                status=TopicStatus.COMPLETED
            ).values_list('topic_id', flat=True)

            not_done = all_topics.exclude(id__in=completed_topic_ids)
            for t in not_done[:10]:
                pdf_url = request.build_absolute_uri(t.presentation_file.url) if t.presentation_file else None
                missed_topics.append({
                    'topic_id': t.id,
                    'module_title': t.module.title,
                    'topic_title': t.title,
                    'presentation_title': t.presentation_title,
                    'presentation_pdf_url': pdf_url,
                    'slides_count': t.slides_count,
                    'duration_hours': float(t.duration_hours)
                })

        # So'nggi uy vazifalari holati
        submissions = AssignmentSubmission.objects.filter(student=student).select_related('assignment').order_by('-submitted_at')[:10]
        recent_assignments = []
        for s in submissions:
            recent_assignments.append({
                'title': s.assignment.title,
                'max_score': s.assignment.max_score,
                'score': s.score,
                'status': s.status,
                'status_label': s.get_status_display(),
                'teacher_feedback': s.teacher_feedback,
                'submitted_at': s.submitted_at
            })

        # So'nggi testlar natijalari
        recent_quizzes = QuizAttempt.objects.filter(student=student).select_related('quiz').order_by('-completed_at')[:10]
        quiz_history = []
        for q in recent_quizzes:
            quiz_history.append({
                'quiz_title': q.quiz.title,
                'score_percentage': float(q.score_percentage),
                'passed': q.passed,
                'points_earned': q.points_earned,
                'completed_at': q.completed_at
            })

        avatar_url = request.build_absolute_uri(student.avatar.url) if student.avatar else None

        return Response({
            'student_info': {
                'id': student.id,
                'full_name': student.full_name,
                'email': student.email,
                'avatar': avatar_url,
                'group_name': group.name if group else "Guruhsiz",
                'teacher_name': group.teacher.full_name if (group and group.teacher) else "Biriktirilmagan",
                'rank_in_group': group_rank,
                'total_points': profile.total_points if profile else 0,
                'attendance_rate': float(profile.attendance_rate) if profile else 100.0,
            },
            'attendance_summary': {
                'rate': float(profile.attendance_rate) if profile else 100.0,
                'absent_count': absent_records.count(),
                'absent_dates': list(absent_records),
            },
            'missed_lessons_to_catch_up': missed_topics,
            'recent_assignments': recent_assignments,
            'recent_quizzes': quiz_history,
        })
