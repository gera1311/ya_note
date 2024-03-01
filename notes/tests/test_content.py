"""Тестирование контента проекта 'YaNote'."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm
from .test_variables import (
    USERNAME_AUTHOR, NOTES_EDIT_URL,
    NOTES_LIST_URL, NOTES_ADD_URL
)

User = get_user_model()


class TestDetailPage(TestCase):
    """Тестовый класс деталей страницы."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для тестов."""
        cls.author = User.objects.create(username=USERNAME_AUTHOR)
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'slug{index}',
                author=cls.author
            )
            for index in range(10)
        ]
        Note.objects.bulk_create(all_notes)

    def test_authorized_user_has_notes(self):
        """Тест на доступность заметок авторизованному пользователю."""
        self.client.force_login(self.author)
        url = reverse(NOTES_LIST_URL)
        response = self.client.get(url)
        self.assertIn('note_list', response.context)

    def test_authorized_user_has_form(self):
        """Тест на доступность форм, авторизованному пользователю."""
        self.client.force_login(self.author)
        note = Note.objects.first()
        urls = (
            (NOTES_ADD_URL, None),
            (NOTES_EDIT_URL, (note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
