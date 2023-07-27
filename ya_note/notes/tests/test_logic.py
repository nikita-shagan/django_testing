from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteEditDeleteCreate(TestCase):
    AUTHOR_NAME = 'Author'
    NOTE_TITLE = 'Note title'
    NOTE_TEXT = 'Note text'
    NOTE_SLUG = 'note_slug'
    NEW_NOTE_TITLE = 'New note title'
    NEW_NOTE_TEXT = 'New note text'
    NEW_NOTE_SLUG = 'new_note_slug'
    READER_NAME = 'Reader'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=cls.AUTHOR_NAME)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.reader = User.objects.create(username=cls.READER_NAME)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.new_form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.add_url, data=self.new_form_data)
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={self.add_url}')
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_create_note(self):
        response = self.author_client.post(
            self.add_url, data=self.new_form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.filter(slug=self.new_form_data['slug']).get()
        self.assertEqual(new_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(new_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(new_note.slug, self.NEW_NOTE_SLUG)
        self.assertEqual(new_note.author, self.author)

    def test_slugs_unique(self):
        new_form_data = self.new_form_data.copy()
        new_form_data['slug'] = self.NOTE_SLUG
        response = self.author_client.post(
            self.add_url, data=new_form_data
        )
        self.assertFormError(
            response, 'form', 'slug', errors=(self.NOTE_SLUG + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_create_note_without_slug(self):
        form_data = self.new_form_data.copy()
        form_data.pop('slug')
        self.author_client.post(self.add_url, data=form_data)
        self.assertEqual(Note.objects.count(), 2)
        expected_slug = slugify(self.new_form_data['title'])
        note = Note.objects.filter(slug=expected_slug).get()
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.edit_url, data=self.new_form_data
        )
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(
            self.edit_url, data=self.new_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
