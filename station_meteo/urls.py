from django.contrib import admin
from django.urls import path
from app.views import HistoryView, HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name="home"),
    path('historique', HistoryView.as_view(), name="history"),
]
