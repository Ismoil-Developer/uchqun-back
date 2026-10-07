from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, UserRole, Group, StudentProfile
from apps.courses.models import Course, Module, Topic, CourseEnrollment, EnrollmentStatus, TopicStatus
from apps.quizzes.models import Quiz, Question, AnswerOption
from apps.assignments.models import Assignment, AssignmentSubmission, SubmissionStatus


class UchqunApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Admin
        self.admin = User.objects.create_superuser(
            email='admin@uchqun.uz',
            password='adminpassword123',
            first_name='Admin',
            last_name='Uchqun'
        )

        # Teacher
        self.teacher = User.objects.create_user(
            email='teacher@uchqun.uz',
            password='teacherpassword123',
            first_name='Sunnatillo',
            last_name='Mentor',
            role=UserRole.TEACHER
        )

        # Group
        self.group = Group.objects.create(name='F-2401', teacher=self.teacher)

        # Parent
        self.parent = User.objects.create_user(
            email='parent@uchqun.uz',
            password='parentpassword123',
            first_name='Ota',
            last_name='Qodirov',
            role=UserRole.PARENT
        )

        # Student
        self.student = User.objects.create_user(
            email='example@uchqun.uz',
            password='password123',
            first_name='Azizbek',
            last_name='Qodirov',
            role=UserRole.STUDENT
        )
        self.student_profile = self.student.student_profile
        self.student_profile.group = self.group
        self.student_profile.parent = self.parent
        self.student_profile.total_points = 850
        self.student_profile.attendance_rate = 98.0
        self.student_profile.save()

        # Course & Modules
        self.course_fe = Course.objects.create(
            title='Frontend Dasturlash',
            slug='frontend-dasturlash',
            description='HTML, CSS, JS',
            technologies=['HTML', 'CSS', 'JavaScript', 'React'],
            order=1
        )
        self.course_be = Course.objects.create(
            title='Backend Dasturlash',
            slug='backend-dasturlash',
            description='Python, Django, SQL',
            technologies=['Python', 'Django', 'SQL'],
            order=2
        )
        self.course_mobile = Course.objects.create(
            title='Mobile Dasturlash',
            slug='mobile-dasturlash',
            description='Flutter, Dart',
            technologies=['Flutter', 'Dart'],
            order=3
        )

        # Enrollments: FE is OPEN, BE is OPEN, Mobile is WAITING
        CourseEnrollment.objects.create(
            student=self.student,
            course=self.course_fe,
            status=EnrollmentStatus.OPEN
        )
        CourseEnrollment.objects.create(
            student=self.student,
            course=self.course_be,
            status=EnrollmentStatus.OPEN
        )
        CourseEnrollment.objects.create(
            student=self.student,
            course=self.course_mobile,
            status=EnrollmentStatus.WAITING
        )

        self.module_html = Module.objects.create(
            course=self.course_fe,
            title='HTML Asoslari',
            order=1,
            lessons_count_display=12,
            topics_count_display=24
        )

        self.topic = Topic.objects.create(
            module=self.module_html,
            title='Metateglar va Semantika',
            order=3,
            lessons_count=5,
            duration_hours=1.5,
            presentation_title='Dars Prezentatsiyasi: Metateglar va SEO asoslari',
            slides_count=18
        )

        # Quiz
        self.quiz = Quiz.objects.create(topic=self.topic, title='Metateglar mini-testi', pass_percentage=60)
        self.q1 = Question.objects.create(quiz=self.quiz, order=1, text="Charsetni aniqlang:", points=10)
        self.opt1 = AnswerOption.objects.create(question=self.q1, order=1, text="A) UTF-8", is_correct=True)
        self.opt2 = AnswerOption.objects.create(question=self.q1, order=2, text="B) ASCII", is_correct=False)

        # Assignment
        self.assignment = Assignment.objects.create(
            topic=self.topic,
            title="Loyiha uchun asosiy metadasturlarni sozlash",
            description="Index.html faylini yarating...",
            max_score=100,
            deadline_text="Muddat: 1 kun qoldi",
            is_daily_featured=True
        )

    def test_01_login_success(self):
        """1-ekran: E-mail va parol orqali tizimga kirish (JWT olish)"""
        url = reverse('auth-login')
        response = self.client.post(url, {
            'email': 'example@uchqun.uz',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'example@uchqun.uz')
        self.assertEqual(response.data['user']['role'], UserRole.STUDENT)

    def test_02_course_list_with_enrollment_status(self):
        """2-ekran: Kurslar ro'yxati, OCHIQ va YOPIQ statuslari, 1-2 ta kurs cheklovi"""
        self.client.force_authenticate(user=self.student)
        url = reverse('courses-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('restriction_notice', response.data)
        courses = response.data['courses']
        self.assertEqual(len(courses), 3)

        fe_course = next(c for c in courses if c['slug'] == 'frontend-dasturlash')
        self.assertEqual(fe_course['enrollment_status'], 'OPEN')
        self.assertTrue(fe_course['is_accessible'])

        mobile_course = next(c for c in courses if c['slug'] == 'mobile-dasturlash')
        self.assertEqual(mobile_course['enrollment_status'], 'WAITING')
        self.assertFalse(mobile_course['is_accessible'])

    def test_03_course_modules(self):
        """3-ekran: Kurs modullari ro'yxati"""
        self.client.force_authenticate(user=self.student)
        url = reverse('course-modules', kwargs={'slug': 'frontend-dasturlash'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course_slug'], 'frontend-dasturlash')
        self.assertEqual(len(response.data['modules']), 1)
        self.assertEqual(response.data['modules'][0]['title'], 'HTML Asoslari')

    def test_04_module_topics_list_and_search(self):
        """4-ekran: Modul mavzulari va mavzu bo'yicha qidiruv"""
        self.client.force_authenticate(user=self.student)
        url = reverse('module-topics', kwargs={'module_id': self.module_html.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['topics']), 1)
        self.assertEqual(response.data['topics'][0]['title'], 'Metateglar va Semantika')

        # Qidiruv testi
        search_res = self.client.get(f"{url}?search=Metateglar")
        self.assertEqual(len(search_res.data['topics']), 1)
        not_found_res = self.client.get(f"{url}?search=MavjudEmas")
        self.assertEqual(len(not_found_res.data['topics']), 0)

    def test_05_topic_detail_presentation(self):
        """5-ekran: Mavzu tafsilotlari, prezentatsiya slaydlar soni va ma'lumotlar"""
        self.client.force_authenticate(user=self.student)
        url = reverse('topic-detail', kwargs={'pk': self.topic.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Metateglar va Semantika')
        self.assertEqual(response.data['slides_count'], 18)
        self.assertEqual(response.data['presentation_title'], 'Dars Prezentatsiyasi: Metateglar va SEO asoslari')

    def test_06_quiz_submit_and_scoring(self):
        """5-ekran: Mini-test topshirish va natijani hisoblash"""
        self.client.force_authenticate(user=self.student)
        url = reverse('quiz-submit', kwargs={'pk': self.quiz.id})
        response = self.client.post(url, {
            'answers': [
                {'question_id': self.q1.id, 'selected_option_id': self.opt1.id}
            ]
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['correct_answers'], 1)
        self.assertEqual(response.data['score_percentage'], 100.0)
        self.assertTrue(response.data['passed'])
        self.assertEqual(response.data['results'][0]['status_badge'], "TO'G'RI")

    def test_07_assignment_daily_featured_and_submit(self):
        """3-ekran banner va 5-ekran: Amaliy topshiriqni yuklash"""
        self.client.force_authenticate(user=self.student)

        # Featured banner
        banner_url = reverse('assignment-daily-featured')
        banner_res = self.client.get(banner_url)
        self.assertEqual(banner_res.status_code, status.HTTP_200_OK)
        self.assertTrue(banner_res.data['has_featured'])

        # Topshiriq yuborish
        submit_url = reverse('assignment-submit', kwargs={'pk': self.assignment.id})
        submit_res = self.client.post(submit_url, {
            'code_text': '<html><head><meta charset="UTF-8"></head></html>',
            'student_comment': 'Topshiriqni muvaffaqiyatli bajardim!'
        })
        self.assertEqual(submit_res.status_code, status.HTTP_200_OK)
        self.assertEqual(submit_res.data['status'], SubmissionStatus.PENDING)

    def test_08_group_leaderboard(self):
        """Guruh reytingi: Azizbek va sinfdoshlar reyting jadvali"""
        self.client.force_authenticate(user=self.student)
        url = reverse('group-leaderboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['group_name'], 'F-2401')
        self.assertGreaterEqual(len(response.data['rankings']), 1)
        self.assertTrue(response.data['rankings'][0]['is_current_user'])

    def test_09_parent_monitoring_dashboard(self):
        """Ota-onalar farzandini nazorat qilish paneli"""
        self.client.force_authenticate(user=self.parent)

        # Farzandlar ro'yxati
        list_url = reverse('parent-children')
        list_res = self.client.get(list_url)
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data['children']), 1)
        self.assertEqual(list_res.data['children'][0]['full_name'], 'Azizbek Qodirov')

        # Bolaning to'liq ko'rsatkichlari paneli
        dash_url = reverse('parent-child-dashboard', kwargs={'student_id': self.student.id})
        dash_res = self.client.get(dash_url)
        self.assertEqual(dash_res.status_code, status.HTTP_200_OK)
        self.assertEqual(dash_res.data['student_info']['full_name'], 'Azizbek Qodirov')
        self.assertIn('attendance_summary', dash_res.data)
        self.assertIn('missed_lessons_to_catch_up', dash_res.data)
        self.assertIn('recent_assignments', dash_res.data)
