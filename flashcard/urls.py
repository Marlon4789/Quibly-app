from django.urls import path
from .views import ChapterListView, ChapterDetailView

urlpatterns = [
    path('capitulos/', ChapterListView.as_view(), name='chapter_list'),
    path('capitulos/<slug:slug>/', ChapterDetailView.as_view(), name='chapter_detail'),
]