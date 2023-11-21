from django import forms
from .models import Sensor

class SensorSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sensors = Sensor.objects.all()
        sensor_choices = [(sensor.id, sensor.name) for sensor in sensors]
        self.fields['sensor_id'] = forms.ChoiceField(
            label='Sélectionnez un capteur',
            choices=[('', 'Choisissez un capteur')] + sensor_choices,
            required=True
        )