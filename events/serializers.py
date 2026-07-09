from rest_framework import serializers

from .models import City, DayProgram, DayScheduleFile, Program, User


class CityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')


class UserSerializer(serializers.ModelSerializer):
    city = CityListSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('user_id', 'is_manager', 'city')


class UserGetOrCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class UserJoinCitySerializer(serializers.Serializer):
    city_id = serializers.IntegerField()


class DayScheduleFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayScheduleFile
        fields = ('id', 'file', 'order')


class DayProgramSerializer(serializers.ModelSerializer):
    schedule_files = DayScheduleFileSerializer(many=True, read_only=True)

    class Meta:
        model = DayProgram
        fields = ('id', 'date', 'schedule_files')


class ProgramSerializer(serializers.ModelSerializer):
    days = DayProgramSerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = (
            'id',
            'city',
            'schedule_text',
            'schedule_file',
            'map_schema',
            'map_description',
            'faq',
            'check_list',
            'days',
        )
