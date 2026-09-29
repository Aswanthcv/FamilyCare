from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from io import BytesIO
from PIL import Image

from .models import FamilyMember

class AuthenticationTests(TestCase):
    def setUp(self):
        self.password = 'Strong-password-123'
        self.user = User.objects.create_user(username='family-one', email='family@example.com', password=self.password)

    def test_dashboard_redirects_anonymous_users_to_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/?next=/')

    def test_registration_creates_user_and_logs_them_in(self):
        response = self.client.post('/register/', {
            'username': 'new-family', 'email': 'new@example.com',
            'password1': 'Another-strong-password-123',
            'password2': 'Another-strong-password-123',
        })
        self.assertRedirects(response, '/')
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTrue(User.objects.filter(username='new-family').exists())

    def test_login_and_logout_work(self):
        response = self.client.post('/login/', {'username': 'family-one', 'password': self.password})
        self.assertRedirects(response, '/')
        response = self.client.get('/')
        self.assertContains(response, 'Welcome, family-one!')
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/login/')
        self.assertNotIn('_auth_user_id', self.client.session)


class FamilyMemberTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='Strong-password-123')
        self.other_user = User.objects.create_user(username='other', password='Strong-password-123')
        self.client.force_login(self.user)

    def member_data(self):
        image_buffer = BytesIO()
        Image.new('RGB', (10, 10), color='blue').save(image_buffer, format='JPEG')
        image = SimpleUploadedFile('profile.jpg', image_buffer.getvalue(), content_type='image/jpeg')
        return {
            'full_name': 'Asha Owner', 'date_of_birth': '1990-05-10', 'sex': 'F',
            'phone': '1234567890', 'email': 'asha@example.com', 'profile_image': image,
            'blood_group': 'O+', 'height': '165', 'weight': '60',
            'medical_conditions': 'None', 'allergies': 'None',
            'current_medications': '', 'emergency_contact': '9999999999', 'additional_notes': '',
        }

    def test_add_view_edit_and_delete_member(self):
        response = self.client.post('/members/add/', self.member_data())
        self.assertEqual(response.status_code, 302)
        member = FamilyMember.objects.get(full_name='Asha Owner')
        self.assertEqual(member.user, self.user)
        self.assertTrue(member.profile_image.name.startswith('profile_images/'))

        self.assertEqual(self.client.get(f'/members/{member.id}/').status_code, 200)
        response = self.client.post(f'/members/{member.id}/edit/', {
            **self.member_data(), 'profile_image': '', 'full_name': 'Asha Updated',
        })
        self.assertEqual(response.status_code, 302)
        member.refresh_from_db()
        self.assertEqual(member.full_name, 'Asha Updated')

        self.assertEqual(self.client.get(f'/members/{member.id}/delete/').status_code, 200)
        response = self.client.post(f'/members/{member.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(FamilyMember.objects.filter(id=member.id).exists())

    def test_user_cannot_access_another_users_member(self):
        member = FamilyMember.objects.create(
            user=self.other_user, full_name='Other Person', date_of_birth='2000-01-01', sex='O',
        )
        self.assertEqual(self.client.get(f'/members/{member.id}/').status_code, 404)
        self.assertEqual(self.client.get(f'/members/{member.id}/edit/').status_code, 404)
        self.assertEqual(self.client.get(f'/members/{member.id}/delete/').status_code, 404)
