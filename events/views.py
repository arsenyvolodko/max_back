from django.db.models import Prefetch
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import City, DayProgram, Program, User
from .serializers import (
    CityListSerializer,
    ProgramSerializer,
    UserGetOrCreateSerializer,
    UserJoinCitySerializer,
    UserSerializer,
)


class CityListView(ListAPIView):
    """GET /api/cities/ — список городов (id + name), по алфавиту."""
    queryset = City.objects.order_by(Lower('name'))
    serializer_class = CityListSerializer


class CityProgramView(APIView):
    """GET /api/cities/<city_id>/program/ — программа города с днями."""

    @extend_schema(responses=ProgramSerializer)
    def get(self, request, city_id):
        program = get_object_or_404(
            Program.objects.select_related('city').prefetch_related(
                Prefetch('days', queryset=DayProgram.objects.order_by('date'))
            ),
            city_id=city_id,
        )
        serializer = ProgramSerializer(program, context={'request': request})
        return Response(serializer.data)


class UserListView(ListAPIView):
    """GET /api/users/list/ — список всех пользователей.

    Поддерживает фильтрацию по городу через query-параметр ?city_id=<id>.
    """
    serializer_class = UserSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='city_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Фильтр по id города',
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = User.objects.select_related('city').all()
        city_id = self.request.query_params.get('city_id')
        if city_id is not None:
            queryset = queryset.filter(city_id=city_id)
        return queryset


class UserGetOrCreateView(APIView):
    """POST /api/users/ — get_or_create пользователя по user_id.

    Возвращает 201 при создании, 200 если уже существовал.
    В ответе город пользователя (id + name) или null.
    """

    @extend_schema(request=UserGetOrCreateSerializer, responses=UserSerializer)
    def post(self, request):
        in_serializer = UserGetOrCreateSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(
            user_id=in_serializer.validated_data['user_id']
        )
        out = UserSerializer(user, context={'request': request})
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(out.data, status=code)


class UserJoinCityView(APIView):
    """POST /api/users/<user_id>/city/ — привязать пользователя к городу.

    Каждый пользователь привязан только к одному городу: если был привязан
    к другому — город просто заменяется.
    """

    @extend_schema(request=UserJoinCitySerializer, responses=UserSerializer)
    def post(self, request, user_id):
        user = get_object_or_404(User, user_id=user_id)
        in_serializer = UserJoinCitySerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        city = get_object_or_404(City, pk=in_serializer.validated_data['city_id'])
        user.city = city
        user.save(update_fields=['city'])
        out = UserSerializer(user, context={'request': request})
        return Response(out.data)
