from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import KEY_LENGTH, ShortURL, sha256_short_key


class ShortURLModelTests(TestCase):
    def test_sha256_short_key(self):
        self.assertEqual(sha256_short_key('abc'), 'ba7816bf8f')

    def test_generates_key_when_missing(self):
        user = User.objects.create_user(username='owner', password='testpass123')
        short_url = ShortURL.objects.create(owner=user, long_url='https://example.com/a')

        self.assertEqual(len(short_url.key), KEY_LENGTH)
        self.assertTrue(all(char in '0123456789abcdef' for char in short_url.key))


class ShortURLViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='testpass123')
        self.other_user = User.objects.create_user(username='bob', password='testpass123')

    def test_register_logs_user_in(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'password1': 'complex-pass-123',
                'password2': 'complex-pass-123',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_anonymous_user_is_redirected_from_list(self):
        response = self.client.get(reverse('shortener:list'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_authenticated_user_can_create_custom_short_url(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('shortener:create'),
            {
                'long_url': 'https://www.djangoproject.com/',
                'custom_key': 'django',
                'expires_at': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ShortURL.objects.filter(owner=self.user, key='django').exists()
        )

    def test_custom_key_must_be_unique(self):
        ShortURL.objects.create(
            owner=self.user,
            long_url='https://example.com/',
            key='taken',
        )
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse('shortener:create'),
            {
                'long_url': 'https://example.org/',
                'custom_key': 'taken',
                'expires_at': '',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already taken')

    def test_user_only_sees_own_urls(self):
        own = ShortURL.objects.create(owner=self.user, long_url='https://own.example/')
        ShortURL.objects.create(owner=self.other_user, long_url='https://other.example/')
        self.client.force_login(self.user)

        response = self.client.get(reverse('shortener:list'))

        self.assertContains(response, own.long_url)
        self.assertNotContains(response, 'https://other.example/')

    def test_redirect_increments_click_count(self):
        short_url = ShortURL.objects.create(
            owner=self.user,
            long_url='https://example.com/landing',
            key='go',
        )

        response = self.client.get(reverse('shortener:redirect', args=[short_url.key]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], short_url.long_url)
        short_url.refresh_from_db()
        self.assertEqual(short_url.click_count, 1)

    def test_expired_url_returns_gone_without_incrementing_clicks(self):
        short_url = ShortURL.objects.create(
            owner=self.user,
            long_url='https://example.com/expired',
            key='old',
            expires_at=timezone.now() - timedelta(hours=1),
        )

        response = self.client.get(reverse('shortener:redirect', args=[short_url.key]))

        self.assertEqual(response.status_code, 410)
        short_url.refresh_from_db()
        self.assertEqual(short_url.click_count, 0)

    def test_owner_can_generate_qr_code(self):
        short_url = ShortURL.objects.create(
            owner=self.user,
            long_url='https://example.com/qr',
            key='qrtest',
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('shortener:qr', args=[short_url.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertGreater(len(response.content), 100)
