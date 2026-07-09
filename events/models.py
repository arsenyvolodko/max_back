from django.db import models

from .fields import HashedFileField


class City(models.Model):
    name = models.CharField('Название', max_length=255)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name


class Program(models.Model):
    city = models.OneToOneField(
        City,
        on_delete=models.CASCADE,
        related_name='program',
        verbose_name='Город',
    )
    schedule_text = models.TextField('Расписание (текст)', blank=True)
    schedule_file = HashedFileField(
        'Расписание (файл)', upload_to='program/schedule/', blank=True, null=True
    )
    map_schema = HashedFileField(
        'Схема (карта)', upload_to='program/map/', blank=True, null=True
    )
    map_description = models.TextField('Описание карты проезда', blank=True)
    faq = models.TextField('FAQ', blank=True)
    check_list = models.TextField('Check-list', blank=True)

    class Meta:
        verbose_name = 'Программа'
        verbose_name_plural = 'Программы'

    def __str__(self):
        return f'Программа — {self.city.name}'


class User(models.Model):
    user_id = models.BigIntegerField('ID пользователя', unique=True)
    is_manager = models.BooleanField('Менеджер', default=False)
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        related_name='users',
        verbose_name='Город',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.user_id)


class DayProgram(models.Model):
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='days',
        verbose_name='Программа',
    )
    date = models.DateField('Дата')

    class Meta:
        verbose_name = 'Программа дня'
        verbose_name_plural = 'Программы дней'
        ordering = ('date',)

    def __str__(self):
        return f'{self.program.city.name} — {self.date}'


class DayScheduleFile(models.Model):
    day = models.ForeignKey(
        DayProgram,
        on_delete=models.CASCADE,
        related_name='schedule_files',
        verbose_name='Программа дня',
    )
    file = HashedFileField(
        'Расписание дня (файл)', upload_to='day_program/schedule/'
    )
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)

    class Meta:
        verbose_name = 'Файл расписания дня'
        verbose_name_plural = 'Файлы расписания дня'
        ordering = ('order', 'id')

    def __str__(self):
        return f'{self.day} — {self.file.name}'
