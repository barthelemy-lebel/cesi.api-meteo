from django.db import models

class Sensor(models.Model):
    name = models.CharField(max_length=45, default=f"Sensor-{id}", unique=True)
    type = models.IntegerField(default=2)
    status = models.IntegerField(default=2)
    lat = models.FloatField(default=0.0)
    long = models.FloatField(default=0.0)
    
    def __str__(self):
        return self.name

class History(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidity = models.FloatField()
    battery_level = models.IntegerField()
    signal_rssi = models.FloatField()
    update_time = models.DateTimeField()

class User(models.Model):
    name = models.CharField(max_length=45, default="", null=False)
    email = models.CharField(max_length=45, default="", unique=True, null=False)
