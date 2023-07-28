from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    AUTHOR_NAME = 'Author'
    READER_NAME = 'Reader'
    NOTE_TEXT = 'Text'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=cls.AUTHOR_NAME)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username=cls.READER_NAME)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(text=cls.NOTE_TEXT, author=cls.author)
        cls.urls_for_anonymous_users = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        cls.urls_for_authed_users = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        cls.urls_for_author = (
            ('notes:edit', (cls.note.slug,)),
            ('notes:detail', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        )

    def check_pages_availability(self, client, urls, status):
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = client.get(url)
                self.assertEqual(response.status_code, status)

    def test_pages_availability_for_anonymous(self):
        self.check_pages_availability(
            self.client, self.urls_for_anonymous_users, HTTPStatus.OK
        )

    def test_redirect_for_anonymous(self):
        login_url = reverse('users:login')
        urls = self.urls_for_authed_users + self.urls_for_author
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_availability_for_authed(self):
        self.check_pages_availability(
            self.reader_client, self.urls_for_authed_users, HTTPStatus.OK
        )

    def test_note_page_availability(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for client, status in users_statuses:
            self.check_pages_availability(client, self.urls_for_author, status)
