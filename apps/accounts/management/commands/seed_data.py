from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from apps.accounts.models import User, UserRole, Group, StudentProfile, ParentProfile
from apps.courses.models import Course, CourseEnrollment, Module, Topic, TopicProgress, EnrollmentStatus, TopicStatus
from apps.quizzes.models import Quiz, Question, AnswerOption, QuizAttempt, StudentQuestionAnswer
from apps.assignments.models import Assignment, AssignmentSubmission, SubmissionStatus
from apps.analytics.models import Attendance, AttendanceStatus, AchievementBadge, StudentBadge
from apps.communication.models import Announcement, Notification, NotificationType


class Command(BaseCommand):
    help = "Populate database with initial realistic Figma data for UCHQUN LMS"

    def handle(self, *args, **options):
        self.stdout.write("UCHQUN boshlang'ich ma'lumotlarini yuklash boshlandi...")

        # 1. Admin yaratish
        admin_user, _ = User.objects.get_or_create(
            email='admin@uchqun.uz',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Uchqun',
                'role': UserRole.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # 2. Mentor / O'qituvchi yaratish
        teacher, _ = User.objects.get_or_create(
            email='teacher@uchqun.uz',
            defaults={
                'first_name': 'Sunnatillo',
                'last_name': 'Ustoz',
                'role': UserRole.TEACHER,
                'is_staff': True,
                'phone_number': '+998901234567'
            }
        )
        teacher.set_password('teacher123')
        teacher.save()

        # 3. Kurslar (Figma 2-ekran)
        course_frontend, _ = Course.objects.get_or_create(
            slug='frontend-dasturlash',
            defaults={
                'title': 'Frontend Dasturlash',
                'description': 'Veb-sahifalar va interaktiv foydalanuvchi interfeyslarini yaratish',
                'icon': 'code',
                'technologies': ['HTML', 'CSS', 'JavaScript', 'React'],
                'order': 1,
                'is_active': True
            }
        )

        course_backend, _ = Course.objects.get_or_create(
            slug='backend-dasturlash',
            defaults={
                'title': 'Backend Dasturlash',
                'description': "Ma'lumotlar bazasi, serverlar va dasturiy ta'minot arxitekturasi",
                'icon': 'database',
                'technologies': ['Python', 'Node.js', 'Django', 'SQL'],
                'order': 2,
                'is_active': True
            }
        )

        course_mobile, _ = Course.objects.get_or_create(
            slug='mobile-dasturlash',
            defaults={
                'title': 'Mobile Dasturlash',
                'description': 'Android va iOS tizimlari uchun zamonaviy ilovalar yaratish',
                'icon': 'mobile',
                'technologies': ['Flutter', 'Dart', 'React Native'],
                'order': 3,
                'is_active': True
            }
        )

        course_computer, _ = Course.objects.get_or_create(
            slug='kompyuter-savodxonligi',
            defaults={
                'title': 'Kompyuter Savodxonligi',
                'description': 'IT asboblar, Windows, Office dasturlari va xavfsizlik asoslari',
                'icon': 'desktop',
                'technologies': ['Windows', 'MS Office', 'IT Foundation'],
                'order': 4,
                'is_active': True
            }
        )

        # 4. Guruh yaratish (F-2401)
        group, _ = Group.objects.get_or_create(
            name='F-2401',
            defaults={
                'description': "Frontend yo'nalishi 2026-yil 1-guruh",
                'teacher': teacher,
                'telegram_group_url': 'https://t.me/uchqun_f2401'
            }
        )

        # 5. Ota-ona foydalanuvchisi
        parent_user, _ = User.objects.get_or_create(
            email='parent@uchqun.uz',
            defaults={
                'first_name': 'Akmal',
                'last_name': 'Qodirov',
                'role': UserRole.PARENT,
                'phone_number': '+998909876543'
            }
        )
        parent_user.set_password('parent123')
        parent_user.save()

        # 6. Bosh o'quvchi (Azizbek Qodirov - Figma dizayndagi asosiy qahramon)
        student_user, _ = User.objects.get_or_create(
            email='example@uchqun.uz',
            defaults={
                'first_name': 'Azizbek',
                'last_name': 'Qodirov',
                'role': UserRole.STUDENT,
                'phone_number': '+998935554433'
            }
        )
        student_user.set_password('password123')
        student_user.save()

        # O'quvchi profili
        st_profile, _ = StudentProfile.objects.get_or_create(
            user=student_user,
            defaults={
                'group': group,
                'parent': parent_user,
                'total_points': 850,
                'attendance_rate': 98.0,
                'completed_tasks_count': 8,
                'passed_quizzes_count': 12,
                'bio': "Yosh dasturchi, Frontend va Backend o'rganuvchisi."
            }
        )
        st_profile.group = group
        st_profile.parent = parent_user
        st_profile.total_points = 850
        st_profile.save()

        # Qo'shimcha sinfdoshlar (Guruh reytingi - Leaderboard uchun)
        classmates_data = [
            ('jasurbek@uchqun.uz', 'Jasurbek', 'Toirov', 820, 96.0, 7),
            ('madina@uchqun.uz', 'Madina', 'Karimova', 790, 100.0, 7),
            ('shahzod@uchqun.uz', 'Shahzod', 'Alimov', 710, 92.0, 5),
            ('dilnoza@uchqun.uz', 'Dilnoza', 'Rahimova', 680, 90.0, 4),
        ]
        for c_email, c_first, c_last, c_pts, c_att, c_tasks in classmates_data:
            c_u, _ = User.objects.get_or_create(
                email=c_email,
                defaults={
                    'first_name': c_first,
                    'last_name': c_last,
                    'role': UserRole.STUDENT,
                }
            )
            c_u.set_password('student123')
            c_u.save()
            cp, _ = StudentProfile.objects.get_or_create(user=c_u)
            cp.group = group
            cp.total_points = c_pts
            cp.attendance_rate = c_att
            cp.completed_tasks_count = c_tasks
            cp.save()

        # 7. Kursga yozilishlar (Figma 2-ekran cheklovlari)
        # Frontend: OCHIQ
        CourseEnrollment.objects.update_or_create(
            student=student_user,
            course=course_frontend,
            defaults={'status': EnrollmentStatus.OPEN, 'progress_percentage': 60.0}
        )
        # Backend: OCHIQ
        CourseEnrollment.objects.update_or_create(
            student=student_user,
            course=course_backend,
            defaults={'status': EnrollmentStatus.OPEN, 'progress_percentage': 15.0}
        )
        # Mobile: Yopiq (Navbat kutilmoqda)
        CourseEnrollment.objects.update_or_create(
            student=student_user,
            course=course_mobile,
            defaults={'status': EnrollmentStatus.WAITING, 'progress_percentage': 0.0}
        )
        # Kompyuter savodxonligi: Yopiq (Navbat kutilmoqda)
        CourseEnrollment.objects.update_or_create(
            student=student_user,
            course=course_computer,
            defaults={'status': EnrollmentStatus.WAITING, 'progress_percentage': 0.0}
        )

        # 8. Modullar (Figma 3-ekran)
        mod_html, _ = Module.objects.get_or_create(
            course=course_frontend,
            title='HTML Asoslari',
            defaults={
                'order': 1,
                'lessons_count_display': 12,
                'topics_count_display': 24,
                'description': "Boshlang'ich veb-texnologiya poydevorini mustahkamlang."
            }
        )

        mod_css, _ = Module.objects.get_or_create(
            course=course_frontend,
            title='CSS Visual Dizayn',
            defaults={
                'order': 2,
                'lessons_count_display': 18,
                'topics_count_display': 36,
                'description': "Zamonaviy veb-dizayn, Flexbox, Grid va animatsiyalar."
            }
        )

        mod_js, _ = Module.objects.get_or_create(
            course=course_frontend,
            title='JavaScript Dasturlash',
            defaults={
                'order': 3,
                'lessons_count_display': 24,
                'topics_count_display': 48,
                'description': "Interaktivlik, DOM, mantiq va asinxron so'rovlar."
            }
        )

        # 9. Mavzular (Figma 4-ekran - HTML moduli mavzulari)
        topics_info = [
            (1, "HTMLga kirish", 4, 1.5, TopicStatus.COMPLETED, 100),
            (2, "Teglar va Atributlar", 6, 1.5, TopicStatus.COMPLETED, 100),
            (3, "Metateglar va Semantika", 5, 1.5, TopicStatus.IN_PROGRESS, 75),
            (4, "Formalar va Inputlar", 8, 1.5, TopicStatus.NOT_STARTED, 20),
            (5, "Multimedia va Audio/Video", 4, 1.5, TopicStatus.LOCKED, 0),
            (6, "HTML5 API va Geolocation", 6, 1.5, TopicStatus.LOCKED, 0),
        ]

        topic_meta = None
        for order, title, l_count, dur, st_status, prog_pct in topics_info:
            t, _ = Topic.objects.get_or_create(
                module=mod_html,
                order=order,
                defaults={
                    'title': title,
                    'lessons_count': l_count,
                    'duration_hours': dur,
                    'presentation_title': f"Dars Prezentatsiyasi: {title}",
                    'slides_count': 18,
                    'description': f"{title} bo'yicha batafsil darslik va video qo'llanma.",
                    'source_code_snippet': "<!DOCTYPE html>\n<html lang=\"uz\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>Uchqun Dars</title>\n</head>\n<body>\n  <h1>Uchqun IT Academy</h1>\n</body>\n</html>"
                }
            )
            if order == 3:
                topic_meta = t
                t.presentation_title = "Dars Prezentatsiyasi: Metateglar va SEO asoslari"
                t.save()

            # Student progress
            TopicProgress.objects.update_or_create(
                student=student_user,
                topic=t,
                defaults={
                    'status': st_status,
                    'progress_percentage': prog_pct,
                    'slides_viewed': 3 if order == 3 else (18 if prog_pct == 100 else 0)
                }
            )

        # 10. Mini-testlar (Figma 5-ekran)
        if topic_meta:
            quiz, _ = Quiz.objects.get_or_create(
                topic=topic_meta,
                title="Metateglar va Semantika mini-testi",
                defaults={'pass_percentage': 60}
            )

            # Savol #1: Charsetni aniqlang: (TO'G'RI javob: A) UTF-8)
            q1, _ = Question.objects.get_or_create(
                quiz=quiz,
                order=1,
                defaults={
                    'text': "Charsetni aniqlang:",
                    'explanation': "O'zbek va xalqaro belgilarni to'g'ri ko'rsatish uchun UTF-8 standarti qo'llaniladi.",
                    'points': 10
                }
            )
            AnswerOption.objects.get_or_create(question=q1, order=1, text="A) UTF-8", defaults={'is_correct': True})
            AnswerOption.objects.get_or_create(question=q1, order=2, text="B) ASCII", defaults={'is_correct': False})
            AnswerOption.objects.get_or_create(question=q1, order=3, text="C) ISO-8859", defaults={'is_correct': False})
            AnswerOption.objects.get_or_create(question=q1, order=4, text="D) Windows-1251", defaults={'is_correct': False})

            # Savol #2: Viewport nima?
            q2, _ = Question.objects.get_or_create(
                quiz=quiz,
                order=2,
                defaults={
                    'text': "Viewport nima?",
                    'explanation': "Viewport - bu brauzerning ko'rinib turgan maydoni (ekran o'lchami).",
                    'points': 10
                }
            )
            AnswerOption.objects.get_or_create(question=q2, order=1, text="A) Server port raqami", defaults={'is_correct': False})
            AnswerOption.objects.get_or_create(question=q2, order=2, text="B) Ekran o'lchami", defaults={'is_correct': True})
            AnswerOption.objects.get_or_create(question=q2, order=3, text="C) Shrift bazasi", defaults={'is_correct': False})
            AnswerOption.objects.get_or_create(question=q2, order=4, text="D) CSS rang palitrasi", defaults={'is_correct': False})

            # Savol #3: Description tegi qayerda yoziladi?
            q3, _ = Question.objects.get_or_create(
                quiz=quiz,
                order=3,
                defaults={
                    'text': "Description tegi qayerda yoziladi?",
                    'explanation': "Barcha metateglar <head> tegi ichida joylashishi lozim.",
                    'points': 10
                }
            )
            AnswerOption.objects.get_or_create(question=q3, order=1, text="A) <body> ichida", defaults={'is_correct': False})
            AnswerOption.objects.get_or_create(question=q3, order=2, text="B) <footer> ichida", defaults={'is_correct': False})
            AnswerOption.objects.get_or_create(question=q3, order=3, text="C) <script> ichida", defaults={'is_correct': False})
            AnswerOption.objects.get_or_create(question=q3, order=4, text="D) <head> ichida", defaults={'is_correct': True})

            # Azizbek uchun 1-savol yechilgan (TO'G'RI)
            attempt, _ = QuizAttempt.objects.get_or_create(
                student=student_user,
                quiz=quiz,
                attempt_number=1,
                defaults={
                    'total_questions': 3,
                    'correct_answers': 1,
                    'score_percentage': 33.33,
                    'points_earned': 10,
                    'passed': False
                }
            )
            correct_opt = q1.options.filter(is_correct=True).first()
            if correct_opt:
                StudentQuestionAnswer.objects.get_or_create(
                    attempt=attempt,
                    question=q1,
                    defaults={'selected_option': correct_opt, 'is_correct': True}
                )

            # 11. Amaliy Topshiriq (Figma 5-ekran)
            assignment, _ = Assignment.objects.get_or_create(
                title="Loyiha uchun asosiy metadasturlarni sozlash",
                topic=topic_meta,
                defaults={
                    'description': "Index.html faylini yarating va unga SEO uchun muhim bo'lgan description, keywords hamda Open Graph metataglarni qo'shing.",
                    'max_score': 100,
                    'deadline_text': "Muddat: 1 kun qoldi",
                    'is_daily_featured': False,
                }
            )

        # 12. Dashboard Banner Asosiy Topshirig'i (Figma 3-ekran)
        if topic_meta:
            featured_assign, _ = Assignment.objects.get_or_create(
                title="Portfolio loyihasini yakunlash",
                defaults={
                    'topic': topic_meta,
                    'description': "HTML va CSS yordamida o'zingizning shaxsiy portfolio loyihangizni yarating va GitHub Pages-ga joylang.",
                    'max_score': 100,
                    'deadline_text': "Muddat: 1 kun qoldi",
                    'is_daily_featured': True,
                    'banner_subtitle': "Haftalik amaliy topshiriq topshirish vaqti tugashiga 1 kun qoldi."
                }
            )

        # 13. Davomat yozuvlari (Ota-onalar ko'rishi uchun)
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(1, 10)]
        for d in dates:
            Attendance.objects.get_or_create(
                student=student_user,
                group=group,
                date=d,
                defaults={
                    'status': AttendanceStatus.PRESENT,
                    'teacher_note': "Darsda faol qatnashdi.",
                    'recorded_by': teacher
                }
            )

        # 14. E'lonlar va Bildirishnomalar
        Announcement.objects.get_or_create(
            title="Haftalik amaliy topshiriqlar bo'yicha ko'rsatma",
            defaults={
                'content': "Hurmatli bilimdonlar, topshiriqlarni belgilangan muddatda skrinshot yoki GitHub havolasi bilan yuklashni unutmang!",
                'group': group,
                'author': teacher,
                'is_pinned': True
            }
        )

        Notification.objects.get_or_create(
            recipient=student_user,
            title="Amaliy topshiriq qo'shildi",
            defaults={
                'message': "Metateglar va Semantika mavzusi bo'yicha yangi amaliy topshiriq e'lon qilindi.",
                'notification_type': NotificationType.ASSIGNMENT
            }
        )

        self.stdout.write(self.style.SUCCESS("UCHQUN boshlang'ich ma'lumotlari muvaffaqiyatli yaratildi!"))
        self.stdout.write(self.style.NOTICE("Test hisoblari:"))
        self.stdout.write("  Admin:     admin@uchqun.uz / admin123")
        self.stdout.write("  O'qituvchi: teacher@uchqun.uz / teacher123")
        self.stdout.write("  O'quvchi:  example@uchqun.uz / password123")
        self.stdout.write("  Ota-ona:   parent@uchqun.uz / parent123")
