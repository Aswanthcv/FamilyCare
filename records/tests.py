from django.contrib.auth.models import User
from django.test import TestCase

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
