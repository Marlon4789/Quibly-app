# flashcard/admin.py

from django.contrib import admin
from .models import Flashcard, Chapter


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """Configuración del admin para los capítulos."""
    list_display = (
        'title',
        'slug',
    )
   
    search_fields = (
        'title',
        'slug',
    )
    prepopulated_fields = {
        'slug': ('title',),
    }
    filter_horizontal = (
        'cards',
    )
    fieldsets = (
        ('Datos generales', {
            'fields': ('title', 'description', 'slug'),
        }),
        ('Tarjetas del capítulo', {
            'fields': ('cards',),
        }),
            
    )


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    """Configuración del admin para las flashcards."""
    list_display = (
        'id',
        'category',
        'word_english',
        'word_spanish',
        'mean_english',
        'mean_espanish',
        'viewed',
        'mark_as',
    )
    list_filter = (
        'category',
        'viewed',
        'mark_as',
    )
    search_fields = (
        'word_english',
        'word_spanish',
        'category',
    )
    list_editable = (
        'viewed',
        'mark_as',
    )
    prepopulated_fields = {
        'slug': ('category', 'word_english'),
    }
    ordering = (
        'category',
        'word_english',
    )
    readonly_fields = (
        'id',
    )
    fieldsets = (
        ('Identidad', {
            'fields': ('id', 'category', 'slug'),
        }),
        ('Contenido principal', {
            'fields': (
                'word_english',
                'word_spanish',
                'ipa_english',
                'ipa_spanish',
                'content',
                'mean_english',
                'mean_espanish',
            ),
        }),
        ('Media', {
            'fields': (
                'image_url',
                'audio_english',
                'audio_spanish',
            ),
        }),
        ('Estado', {
            'fields': ('viewed', 'mark_as'),
        }),
    )
