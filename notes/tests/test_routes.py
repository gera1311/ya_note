"""Тестирование маршрутов проекта 'YaNote'."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from .test_variables import (
    USERNAME_AUTHOR, USERNAME_RANDOM,
    NOTES_HOME_URL, NOTES_EDIT_URL, NOTES_DELETE_URL,
    NOTES_DETAIL_URL, NOTES_LIST_URL, NOTES_SUCCESS_URL,
    NOTES_ADD_URL, USERS_LOGIN_URL, USERS_LOGOUT_URL,
    USERS_SIGNUP_URL
)

User = get_user_model()


class TestRotes(TestCase):
    """Тестовый класс для маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры тестов."""
        cls.author = User.objects.create(
            username=USERNAME_AUTHOR
        )
        cls.other_user = User.objects.create(
            username=USERNAME_RANDOM
        )
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='notes_1',
            author=cls.author
        )

    def test_pages_availability(self):
        """Тест доступа страниц для неавторизованных пользователей."""
        urls = (
            (NOTES_HOME_URL, None),
            (USERS_LOGIN_URL, None),
            (USERS_LOGOUT_URL, None),
            (USERS_SIGNUP_URL, None)
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_authorized(self):
        """Тест доступа страниц для авторизованных пользователей."""
        urls = (
            (NOTES_HOME_URL, None),
            (NOTES_LIST_URL, None),
            (NOTES_SUCCESS_URL, None),
            (USERS_LOGIN_URL, None),
            (USERS_LOGOUT_URL, None),
            (USERS_SIGNUP_URL, None)
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_notes_change_and_view(self):
        """Тест доступа к редактированию и просмоту заметок."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.other_user, HTTPStatus.NOT_FOUND)
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (
                NOTES_EDIT_URL,
                NOTES_DELETE_URL,
                NOTES_DETAIL_URL
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректа для анонимных польователей."""
        login_url = reverse(USERS_LOGIN_URL)
        urls = (
            (NOTES_EDIT_URL, (self.notes.slug,)),
            (NOTES_DELETE_URL, (self.notes.slug,)),
            (NOTES_DETAIL_URL, (self.notes.slug,)),
            (NOTES_LIST_URL, None),
            (NOTES_SUCCESS_URL, None),
            (NOTES_ADD_URL, None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
