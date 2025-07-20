from django.contrib import admin
from .models import Test  # Import the Test model


# testapp/admin.py

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}   # si tienes slug
    filter_horizontal   = ('questions',)         # interfaz de doble lista
    list_display        = ('title', 'num_questions')
