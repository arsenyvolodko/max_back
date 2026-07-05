from django.urls import path

from .views import (
    CityListView,
    CityProgramView,
    UserGetOrCreateView,
    UserJoinCityView,
    UserListView,
)

urlpatterns = [
    path('cities/', CityListView.as_view(), name='city-list'),
    path('cities/<int:city_id>/program/', CityProgramView.as_view(), name='city-program'),
    path('users/list/', UserListView.as_view(), name='user-list'),
    path('users/', UserGetOrCreateView.as_view(), name='user-get-or-create'),
    path('users/<int:user_id>/city/', UserJoinCityView.as_view(), name='user-join-city'),
]
