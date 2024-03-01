"""Проверка логики сайта."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
from .test_variables import (
    USERNAME_AUTHOR, USERNAME_RANDOM, NOTES_EDIT_URL, NOTES_DELETE_URL,
    NOTES_SUCCESS_URL, NOTES_ADD_URL
)

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты, связанные с логикой создания заметок."""

    NOTE_TITLE = 'Новая заметка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'slug_1'

    @classmethod
    def setUpTestData(cls):
        """Необходимые фикстуры для тестов."""
        cls.user = User.objects.create(username=USERNAME_AUTHOR)
        cls.url = reverse(NOTES_ADD_URL)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        """Тест создания заметки анонимным пользователем."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_authorized_user_cant_create_note(self):
        """Тест создания заметки авторизованным пользователем."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)


class TestNoteEditDelete(TestCase):
    """Тесты, связанные с логикой редактирования и удаления заметок."""

    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'slug_1'
    NEW_NOTE_TEXT = 'Обновленный текст заметки'
    NEW_NOTE_TITLE = 'Обновленный заголовок заметки'
    NEW_NOTE_SLUG = 'new_slug_1'

    @classmethod
    def setUpTestData(cls):
        """Необходимые фикстуры для тестов."""
        cls.author = User.objects.create(username=USERNAME_AUTHOR)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_user = User.objects.create(username=USERNAME_RANDOM)
        cls.other_user_client = Client()
        cls.other_user_client.force_login(cls.other_user)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

        cls.url_success_change = reverse(NOTES_SUCCESS_URL)

        cls.edit_note = reverse(NOTES_EDIT_URL, kwargs={'slug': cls.note.slug})
        cls.delete_note = reverse(
            NOTES_DELETE_URL, kwargs={'slug': cls.note.slug}
        )
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG
        }

    def test_author_can_delete_note(self):
        """Тест удаления заметки автором заметки."""
        response = self.author_client.delete(self.delete_note)
        self.assertRedirects(response, self.url_success_change)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Тест удаления заметки другим пользователем."""
        response = self.other_user_client.delete(self.delete_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        """Тест редактирования заметки автором."""
        response = self.author_client.post(self.edit_note, data=self.form_data)
        self.assertRedirects(response, self.url_success_change)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_user_cant_edit_note_of_anothor_user(self):
        """Тест редактирования заметки другим пользователем."""
        response = self.other_user_client.post(
            self.edit_note, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)

    def test_not_unique_slug(self):
        """Тест создания неуникального слага."""
        form_data = {
            'title': 'Заметка 2',
            'slug': self.NOTE_SLUG,
        }
        url = reverse(NOTES_ADD_URL)
        response = self.author_client.post(url, data=form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)
