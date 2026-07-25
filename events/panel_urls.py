from django.contrib.auth.views import LogoutView
from django.urls import path

from . import panel

app_name = 'panel'

urlpatterns = [
    path('login/', panel.PanelLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='panel:login'), name='logout'),
    path('', panel.program_list, name='list'),
    path('city/<int:city_id>/', panel.city_detail, name='city'),
    path('day/<int:day_id>/', panel.day_detail, name='day'),
    path(
        'day/<int:day_id>/file/<int:file_id>/delete/',
        panel.day_file_delete,
        name='day-file-delete',
    ),
]
