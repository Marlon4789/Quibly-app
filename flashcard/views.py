# flashcard/views.py

from django import forms
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, FormView

from .models import Chapter, Flashcard


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
    """
    Muestra las flashcards de un capítulo, permite navegación anterior/siguiente
    y marca cada tarjeta como vista.
    """
    model = Chapter
    template_name = 'flashcard/chapter_detail.html'
    form_class = StudyForm
    context_object_name = 'chapter'

    def dispatch(self, request, *args, **kwargs):
        # cargar el capítulo
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
        if pos < len(self.cards):
            ctx.update({
                'card': self.cards[pos],
                'pos': pos + 1,
                'total': len(self.cards),
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

        # marcar la tarjeta actual
        if pos < len(self.cards):
            card = self.cards[pos]
            card.viewed = True
            card.mark_as = form.cleaned_data['mark_as']
            card.save()
            self.request.session[pos_key] = pos + 1

        return super().form_valid(form)

    def get_success_url(self):
        pos_key = f'pos_{self.object.pk}'
        pos = self.request.session.get(pos_key, 0)
        # si llegamos al final, si show_test redirige al test; si no, a lista
        if pos >= len(self.cards):
            if self.object.show_test and self.object.test:
                return reverse('chapter_test', args=[self.object.slug])
            return reverse('chapter_list')
        return reverse('chapter_detail', args=[self.object.slug])


class ChapterTestView(DetailView, FormView):
    model               = Chapter
    template_name       = 'flashcard/chapter_test.html'
    form_class          = forms.Form  # o tu clase dinámica, da igual
    context_object_name = 'chapter'

    def dispatch(self, request, *args, **kwargs):
        # Aseguramos que self.object esté definido
        self.object = self.get_object()
        # Si el test no está configurado o no está habilitado, lo llevamos de vuelta
        if not self.object.show_test or not self.object.test:
            return redirect('chapter_detail', slug=self.object.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        questions = self.object.test.questions.all()[: self.object.test.num_questions]
        fields = {}
        for i, card in enumerate(questions, start=1):
            fld = forms.CharField(
                label=f"What is the correct answer to the meaning of '{card.mean_english}'?",
                max_length=200
            )
            fld.correct_answer = card.word_english  # Guardamos la respuesta correcta
            fields[f'q{i}'] = fld
        return type('DynamicTestForm', (forms.Form,), fields)

    def get_form(self, form_class=None):
        FormCls = self.get_form_class()
        return FormCls(**self.get_form_kwargs())

    def form_valid(self, form):
        questions = self.object.test.questions.all()[: self.object.test.num_questions]
        correct = 0
        for i, card in enumerate(questions, start=1):
            resp = form.cleaned_data.get(f'q{i}', '').strip().lower()
            if resp == card.word_english.strip().lower():
                correct += 1
        passed = (correct == len(questions))
        return self.render_to_response(self.get_context_data(
            passed=passed,
            correct=correct,
            total=len(questions)
        ))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # usamos self.object (ya cargado en dispatch) y los flags que pasamos
        ctx.update({
            'passed':  kwargs.get('passed'),
            'correct': kwargs.get('correct', 0),
            'total':   kwargs.get('total', 0),
        })
        return ctx
