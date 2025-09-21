from django.urls import path
from .views import ChapterListView, ChapterDetailView, ChapterFinishedView, chapter_restart
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('capitulos/', ChapterListView.as_view(), name='chapter_list'),
    path('capitulos/<slug:slug>/', ChapterDetailView.as_view(), name='chapter_detail'),
    path('capitulos/<slug:slug>/finished/', ChapterFinishedView.as_view(), name='chapter_finished'),
    path('capitulos/<slug:slug>/restart/', chapter_restart, name='chapter_restart'),
]