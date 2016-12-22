from django.db import models

# Create your models here.
class Bmp180(models.Model):
	ts = models.DateTimeField(primary_key=True),
	temperature = models.IntegerField(),
	pressure = models.IntegerField(),
	seapressure = models.IntegerField(),

class Am2315(models.Model):
	ts = models.DateTimeField(primary_key=True),
	temperature = models.IntegerField(),
	humidity = models.IntegerField(),

class Gpio(models.Model):
	ts = models.DateTimeField(primary_key=True),
	port = models.IntegerField(),
	delta = models.DateTimeField(),
