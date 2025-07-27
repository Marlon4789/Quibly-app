from django.db import models
from django.utils.text import slugify
from django.urls import reverse



class Chapter(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug        = models.SlugField(unique=True, blank=True)
    # Permite elegir libremente un conjunto de flashcards en cada capítulo
    cards       = models.ManyToManyField('Flashcard', related_name='chapters', blank=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Capítulo'
        verbose_name_plural = 'Capítulos'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # retorna la URL al detalle usando el name='chapter_detail'
        return reverse('chapter_detail', args=[self.slug])

    def __str__(self):
        return self.title





class Flashcard(models.Model):
    CATEGORY_CHOICES = [
        ('phrasal_verb', 'Phrasal verb'),
        ('irregular_verb', 'Irregular verb'),
        ('verb', 'Verb'),
        ('word', 'Word'),
        # Añade más categorías según necesites
    ]

    MARCAR_CHOICES = [
        ('review', 'Review'),
        ('learned', 'Learned'),
    ]

    id = models.AutoField(primary_key=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='word',
    )
    mean_english = models.TextField(blank=True)
    mean_espanish = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    word_english = models.CharField(max_length=200)
    word_spanish = models.CharField(max_length=200)
    ipa_english = models.CharField('Pronunciation IPA (EN)', max_length=200, blank=True)
    ipa_spanish = models.CharField('Pronunciation IPA (ES)', max_length=200, blank=True)
    audio_english = models.FileField(upload_to='audio/english/', blank=True, null=True)
    audio_spanish = models.FileField(upload_to='audio/spanish/', blank=True, null=True)
    content = models.TextField(blank=True)
    viewed = models.BooleanField(default=False)
    mark_as = models.CharField(
        max_length=10,
        choices=MARCAR_CHOICES,
        default='review',
    )
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'
        ordering = ['category', 'word_english']

    def save(self, *args, **kwargs):
        # Generar slug a partir de categoría y palabra en inglés
        if not self.slug:
            base = f"{self.category}-{self.word_english}"
            self.slug = slugify(base)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.word_english} - {self.word_spanish}"


