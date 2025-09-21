from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'is_staff')  # Añadir email aquí
    search_fields = ('username', 'email', 'first_name')  # Añadir email aquí
    ordering = ('username',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
