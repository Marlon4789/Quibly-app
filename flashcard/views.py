# flashcard/views.py

from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView, FormView, TemplateView
from .models import Chapter, Flashcard

def home(request):
    return render(request, "flashcard/home.html")


class ChapterListView(ListView):
    """
    Lista todos los capítulos y marca cuáles están terminados.
    """
    model = Chapter
    template_name = 'flashcard/chapter_list.html'
    context_object_name = 'chapters'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        for ch in ctx['chapters']:
            # consideramos terminado si no quedan flashcards sin ver
            ch.finished = not ch.cards.filter(viewed=False).exists()
        return ctx


class StudyForm(forms.Form):
    """
    Formulario para marcar cada flashcard como 'review' o 'learned'.
    """
    mark_as = forms.ChoiceField(choices=Flashcard.MARCAR_CHOICES)


class ChapterDetailView(DetailView, FormView):
    model = Chapter
    template_name = 'flashcard/chapter_detail.html'
    form_class = StudyForm
    context_object_name = 'chapter'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        pos_key = f'pos_{self.object.pk}'
        restart = request.GET.get('restart') == '1'
        if restart or request.session.get('current_chapter') != self.object.slug:
            request.session[pos_key] = 0
            request.session['current_chapter'] = self.object.slug
        return super().dispatch(request, *args, **kwargs)

    @property
    def cards(self):
        return list(self.object.cards.all())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pos_key = f'pos_{self.object.pk}'
        pos = self.request.session.get(pos_key, 0)
        total = len(self.cards)
        if pos < total:
            ctx.update({
                'card': self.cards[pos],
                'pos': pos + 1,
                'total': total,
                # sugerencia: pasar progress_percent calculado aquí
                'progress_percent': round(((pos + 1) / total) * 100) if total else 0,
                'form': ctx.get('form') or self.get_form(),
            })
        else:
            # Si pos >= total, enviamos contexto vacío (la vista de "finished" se mostrará vía redirect)
            ctx.update({
                'card': None,
                'pos': total,
                'total': total,
                'progress_percent': 100,
                'form': ctx.get('form') or self.get_form(),
            })
        return ctx

    def form_valid(self, form):
        pos_key = f'pos_{self.object.pk}'
        pos = self.request.session.get(pos_key, 0)
        action = self.request.POST.get('action', 'next')

        if action == 'prev':
            # retrocede sin marcar
            new_pos = max(pos - 1, 0)
            self.request.session[pos_key] = new_pos
            return redirect('chapter_detail', slug=self.object.slug)

        # marcar la tarjeta actual (si existe)
        if pos < len(self.cards):
            card = self.cards[pos]
            card.viewed = True
            # si tu formulario tiene mark_as, guárdalo (si no lo tienes, omitir)
            if 'mark_as' in form.cleaned_data:
                card.mark_as = form.cleaned_data.get('mark_as', card.mark_as)
            card.save()
            # avanzamos la posición
            self.request.session[pos_key] = pos + 1

        # Al dejar que super().form_valid() maneje la redirección, get_success_url decidirá a dónde ir
        return super().form_valid(form)

    def get_success_url(self):
        pos_key = f'pos_{self.object.pk}'
        pos = self.request.session.get(pos_key, 0)
        total = len(self.cards)
        if pos >= total:
            # Cuando terminamos, vamos a la vista dedicada de "finished"
            return reverse('chapter_finished', args=[self.object.slug])
        # si no, volvemos a la misma vista para mostrar la siguiente tarjeta (usamos ?pos por claridad)
        return f"{reverse('chapter_detail', args=[self.object.slug])}?pos={pos + 1}"


class ChapterFinishedView(TemplateView):
    template_name = 'flashcard/chapter_finished.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        chapter = get_object_or_404(Chapter, slug=slug)
        total = chapter.cards.count()
        # estadísticas útiles: cuántas marcaron como learned/review
        learned = chapter.cards.filter(mark_as='learned').count()
        review = chapter.cards.filter(mark_as='review').count()
        ctx.update({
            'chapter': chapter,
            'total': total,
            'learned': learned,
            'review': review,
        })
        return ctx

def chapter_restart(request, slug):
    """
    Reinicia el capítulo: marca todas las flashcards relacionadas como no vistas (viewed=False)
    y redirige al capítulo con restart=1 para comenzar desde la primera tarjeta.
    """
    chapter = get_object_or_404(Chapter, slug=slug)
    # marcar todas como no vistas (reset)
    chapter.cards.update(viewed=False)
    # (opcional) resetear mark_as si quieres: chapter.cards.update(mark_as='review')
    # resetear la posición en la sesión también
    pos_key = f'pos_{chapter.pk}'
    request.session[pos_key] = 0
    request.session['current_chapter'] = chapter.slug
    return redirect(f"{reverse('chapter_detail', args=[chapter.slug])}?restart=1")


