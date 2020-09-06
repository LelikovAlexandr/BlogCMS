from datetime import datetime

from django.test import Client, TestCase
from django.urls import reverse

from users.models import User, UserStatus


class UserCreateTest(TestCase):
    fixtures = ['test/users.json', 'test/files.json', 'test/videos.json']

    def setUp(self):
        user = User.objects.get(username='admin')
        user.set_password(1234)
        user.save()

        user = User.objects.get(username='user')
        user.set_password(1234)
        user.save()

    def test_change_user_status(self):
        c = Client()

        c.post(reverse('ChangeUserStatus'), data={'username': 'admin', 'status': 'Second'})
        self.assertEqual(str(User.objects.get(username='admin').status), 'First')

        response = c.login(username='admin', password=1234)
        self.assertTrue(response)

        c.post(reverse('ChangeUserStatus'), data={'username': 'admin', 'status': 'Second'})
        self.assertEqual(str(User.objects.get(username='admin').status), 'Second')

    def test_cancel_recurrent_payments(self):
        c = Client()

        response = c.login(username='user', password=1234)
        self.assertTrue(response)

        c.get(reverse('RecurrentPaymentsCancel'))
        self.assertFalse(User.objects.get(username='user').recurring_payments)

    def test_update_available_video(self):
        c = Client()
        c.login(username='admin', password=1234)
