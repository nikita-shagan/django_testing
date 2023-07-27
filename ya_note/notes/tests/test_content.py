from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    AUTHOR_NAME = 'Author'
    NOTE_TITLE = 'Note title'
    NOTE_TEXT = 'Note text'
    READER_NAME = 'Reader'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=cls.AUTHOR_NAME)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.reader = User.objects.create(username=cls.READER_NAME)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes_list_url = reverse('notes:list')
        cls.notes_add_url = reverse('notes:add')
        cls.notes_edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_list_for_different_users(self):
        clients = ((self.author_client, True), (self.reader_client, False))
        for client, x_note_in_list in clients:
            response = client.get(self.notes_list_url)
            actual_note_in_list = self.note in response.context['object_list']
            self.assertEqual(x_note_in_list, actual_note_in_list)

    def test_pages_contains_form(self):
        urls = (self.notes_add_url, self.notes_edit_url)
        for url in urls:
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
