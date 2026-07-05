from django.contrib import admin

from .models import City, DayProgram, Program, User


class DayProgramInline(admin.TabularInline):
    model = DayProgram
    extra = 1
    ordering = ('date',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order')
    list_editable = ('order',)
    ordering = ('order', 'name')
    search_fields = ('name',)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'city')
    inlines = (DayProgramInline,)


@admin.register(DayProgram)
class DayProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'program', 'date')
    list_filter = ('date',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'city')
    list_filter = ('city',)
    search_fields = ('user_id',)
