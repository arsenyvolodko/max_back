"""Упрощённая панель редактирования для заказчика.

Отдельный простой интерфейс поверх тех же моделей, что и админка.
Позволяет редактировать уже созданные объекты (города/программы/дни),
но не создавать новые. Доступ — по отдельному праву events.access_panel,
не требует is_staff, поэтому админка Django такому пользователю недоступна.
"""
from functools import wraps

from django import forms
from django.contrib.auth.views import LoginView, redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST

from .models import City, DayProgram, DayScheduleFile, Program

# Право, дающее доступ к панели. Пользователь с этим правом и is_staff=False
# может пользоваться панелью, но НЕ может войти в админку Django.
PANEL_PERM = 'events.access_panel'


def panel_required(view):
    """Пускает только активных пользователей с правом доступа к панели.

    Не требует is_staff — поэтому такому пользователю админка недоступна.
    """
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(), reverse('panel:login')
            )
        if not (user.is_active and user.has_perm(PANEL_PERM)):
            raise PermissionDenied('Нет доступа к панели управления.')
        return view(request, *args, **kwargs)

    return _wrapped


class PanelLoginView(LoginView):
    """Отдельный вход в панель (не связан с админкой)."""

    template_name = 'panel/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse('panel:list')

    def get_default_redirect_url(self):
        return reverse_lazy('panel:list')


class ProgramForm(forms.ModelForm):
    """Основные поля программы города с понятными подписями."""

    class Meta:
        model = Program
        fields = ('schedule_file', 'map_schema', 'map_description', 'faq', 'faq_file')
        labels = {
            'schedule_file': 'Полная программа',
            'map_schema': 'Схема (карта)',
            'map_description': 'Описание карты проезда',
            'faq': 'FAQ',
            'faq_file': 'FAQ (файл)',
        }
        widgets = {
            'map_description': forms.Textarea(attrs={'rows': 5}),
            'faq': forms.Textarea(attrs={'rows': 10}),
            # FileInput вместо ClearableFileInput — без «Currently / Clear / Change».
            'schedule_file': forms.FileInput(attrs={'class': 'file-input'}),
            'map_schema': forms.FileInput(attrs={'class': 'file-input'}),
            'faq_file': forms.FileInput(attrs={'class': 'file-input'}),
        }


# Удаление вынесено в отдельный AJAX-эндпоинт (мгновенно, без «Сохранить»),
# поэтому can_delete не нужен — формсет отвечает только за порядок,
# замену и добавление файлов.
DayScheduleFileFormSet = inlineformset_factory(
    DayProgram,
    DayScheduleFile,
    fields=('file', 'order'),
    extra=1,
    can_delete=False,
    widgets={
        'order': forms.HiddenInput(),
        'file': forms.FileInput(attrs={'class': 'file-input'}),
    },
)


@panel_required
def program_list(request):
    """Список всех программ (по городам)."""
    programs = (
        Program.objects.select_related('city')
        .prefetch_related('days')
        .order_by('city__order', 'city__name')
    )
    return render(request, 'panel/program_list.html', {'programs': programs})


@panel_required
def city_detail(request, city_id):
    """Редактирование программы города и список дней."""
    program = get_object_or_404(
        Program.objects.select_related('city').prefetch_related(
            Prefetch('days', queryset=DayProgram.objects.order_by('date'))
        ),
        city_id=city_id,
    )

    if request.method == 'POST':
        form = ProgramForm(request.POST, request.FILES, instance=program)
        if form.is_valid():
            form.save()
            return redirect(reverse('panel:city', args=[city_id]))
    else:
        form = ProgramForm(instance=program)

    return render(
        request,
        'panel/city_detail.html',
        {'program': program, 'city': program.city, 'form': form},
    )


@panel_required
def day_detail(request, day_id):
    """Редактирование только файлов расписания конкретного дня."""
    day = get_object_or_404(
        DayProgram.objects.select_related('program__city'), pk=day_id
    )

    if request.method == 'POST':
        formset = DayScheduleFileFormSet(
            request.POST, request.FILES, instance=day
        )
        if formset.is_valid():
            formset.save()
            return redirect(reverse('panel:day', args=[day_id]))
    else:
        formset = DayScheduleFileFormSet(instance=day)

    return render(
        request,
        'panel/day_detail.html',
        {'day': day, 'city': day.program.city, 'formset': formset},
    )


@panel_required
@require_POST
def day_file_delete(request, day_id, file_id):
    """Мгновенное удаление одного файла расписания дня (по крестику)."""
    obj = get_object_or_404(DayScheduleFile, pk=file_id, day_id=day_id)
    obj.file.delete(save=False)  # убрать файл с диска
    obj.delete()
    return JsonResponse({'ok': True})
