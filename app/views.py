from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .forms import SensorSelectionForm
from .models import Sensor, History
from django.db.models import Avg
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from django.utils import timezone


class HistoryView(View):
    template_name = "history.html"

    def get(self, request):
        form = SensorSelectionForm()
        return render(request, self.template_name, {'form': form, 'history': None})

    def post(self, request):
        form = SensorSelectionForm(request.POST)
        if form.is_valid():
            sensor_id = form.cleaned_data['sensor_id']
            # Tri de l'historique par date de la plus récente à la plus ancienne
            history = History.objects.filter(sensor_id=sensor_id).order_by('-update_time')
            humid_avg = History.objects.aggregate(Avg("humidity"))
            return render(request, self.template_name, {'form': form, 'history': history, 'humid_avg': humid_avg })
        return render(request, self.template_name, {'form': form, 'history': None})

class HomeView(View):
    template_name = "home.html"

    def get(self, request):
        form = SensorSelectionForm()
        return render(request, self.template_name, {'form': form, 'history': None})

    def post(self, request):
        form = SensorSelectionForm(request.POST)
        if form.is_valid():
            sensor_id = form.cleaned_data['sensor_id']

            # Définir la date limite pour les 24 dernières heures
            limit_date = timezone.now() - timezone.timedelta(hours=24)

            # Récupérer l'historique du capteur pour les 24 dernières heures dans l'ordre croissant
            history = History.objects.filter(sensor_id=sensor_id, update_time__gte=limit_date).order_by('update_time')

            # Exclusion des doublons de température, d'humidité et de signal RSSI
            unique_history = []
            prev_temp = prev_humidity = prev_rssi = None
            for entry in history:
                if entry.temperature != prev_temp or entry.humidity != prev_humidity or entry.signal_rssi != prev_rssi:
                    unique_history.append(entry)
                    prev_temp = entry.temperature
                    prev_humidity = entry.humidity
                    prev_rssi = entry.signal_rssi

            # Conversion des données en format JSON pour le graphique
            data = {
                'temperature': [{'x': entry.update_time.isoformat("#", "minutes"), 'y': entry.temperature} for entry in unique_history],
                'humidity': [{'x': entry.update_time.isoformat("#", "minutes"), 'y': entry.humidity} for entry in unique_history],
            }

            return JsonResponse(data)
        return JsonResponse({'error': 'Formulaire non valide'})