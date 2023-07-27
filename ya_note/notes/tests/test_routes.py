from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
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
        cls.reader = User.objects.create(username=cls.READER_NAME)
        cls.note = Note.objects.create(text=cls.NOTE_TEXT, author=cls.author)

    def check_pages_availability(self, urls, status):
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_pages_availability_for_anonymous(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        self.check_pages_availability(urls, HTTPStatus.OK)

    def test_pages_availability_for_authed(self):
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        self.client.force_login(self.reader)
        self.check_pages_availability(urls, HTTPStatus.OK)

    def test_note_availability_for_authed_user(self):
        note_slug = self.note.slug
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ('notes:edit', (note_slug,)),
            ('notes:detail', (note_slug,)),
            ('notes:delete', (note_slug,)),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            self.check_pages_availability(urls, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        note_slug = self.note.slug
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:edit', (note_slug,)),
            ('notes:detail', (note_slug,)),
            ('notes:delete', (note_slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
