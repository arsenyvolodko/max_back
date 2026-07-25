"""Создать/обновить пользователя панели управления.

Такой пользователь получает доступ к /panel/, но НЕ к админке Django
(is_staff=False). Пример:

    python manage.py panel_user zakazchik --password "секрет123"
"""
import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Создать/обновить пользователя панели (без доступа к админке).'

    def add_arguments(self, parser):
        parser.add_argument('username', help='Логин пользователя')
        parser.add_argument(
            '--password',
            help='Пароль (если не указан — спросим интерактивно)',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']

        try:
            perm = Permission.objects.get(
                codename='access_panel',
                content_type__app_label='events',
            )
        except Permission.DoesNotExist:
            raise CommandError(
                'Право events.access_panel не найдено. '
                'Сначала выполните: python manage.py migrate'
            )

        password = options.get('password')
        if not password:
            password = getpass.getpass('Пароль: ')
            if password != getpass.getpass('Повторите пароль: '):
                raise CommandError('Пароли не совпадают.')

        user, created = User.objects.get_or_create(username=username)
        user.is_staff = False       # нет доступа к админке Django
        user.is_superuser = False
        user.is_active = True
        user.set_password(password)
        user.save()
        user.user_permissions.add(perm)

        action = 'создан' if created else 'обновлён'
        self.stdout.write(self.style.SUCCESS(
            f'Пользователь панели «{username}» {action}. '
            f'Вход: /panel/login/ · Админка Django недоступна.'
        ))
