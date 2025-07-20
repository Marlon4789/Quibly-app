from django.db import models
from django.utils.text import slugify
from flashcard.models import Flashcard  # asumimos que flashcard es el nombre de tu app de tarjetas

class Test(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug        = models.SlugField(unique=True, blank=True)
    # Selección de las flashcards que formarán las preguntas
    questions   = models.ManyToManyField(Flashcard, related_name='tests', blank=True)
    # Cuántas de esas preguntas queremos usar (ej.: 3)
    num_questions = models.PositiveIntegerField(default=3)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
