from django.shortcuts import render
from django.http import HttpResponse
from django.db import connections

from .models import Am2315
from .models import Bmp180

# Create your views here.
def index(request):
#	maxts_am2315 = Am2315.objects.using('am2315').raw('select max(ts) from am2315')
#	current_temperature_outside, current_humidity_outside =  Am2315.objects.using('am2315').raw("select (temperature * 1.8 + 32), humidity from am2315 where ts=\'" + maxts_am2315 + "\'")

	cursor = connections['am2315'].cursor()
	cursor.execute('select max(ts) from am2315')
	maxts_am2315 = cursor.fetchone()

	selectstr="select (temperature * 1.8 + 32), humidity from am2315 where ts=\'" + maxts_am2315[0] + "\'"
	cursor.execute("select (temperature * 1.8 + 32), humidity from am2315 where ts=\'" + maxts_am2315[0] + "\'")
	current_temperature_outside, current_humidity_outside = cursor.fetchone()

	current_temperature_outside_formatted = format(current_temperature_outside, '.1f')
	current_humidity_outside_formatted = format(current_humidity_outside, '.1f')

	cursor2 = connections['bmp180'].cursor()
	cursor2.execute('select max(ts) from bmp180')
	maxts_bmp180 = cursor2.fetchone()
	selectstr="select (temperature * 1.8 + 32), pressure from bmp180 where ts=\'" + maxts_bmp180[0] + "\'"
	cursor2.execute(selectstr)

	current_temperature_inside, current_pressure = cursor2.fetchone()
	current_temperature_inside_formatted = format(current_temperature_inside, '.1f')
	current_pressure_formatted = format(current_pressure, '.1f')

	cursor3 = connections['gpio'].cursor()
	cursor3.execute('select date(max(ts)) from io')
	lastday_gpio=cursor3.fetchone()
	selectstr="select (count(ts) * 0.011) from io where port = 13 and date(ts) = \'" + lastday_gpio[0] + "\'"
	cursor3.execute(selectstr)
	rain_today=cursor3.fetchone()
	rain_today_formatted=format(rain_today[0],'.3f')

	context = {
		'current_temperature_outside_formatted': current_temperature_outside_formatted,
		'current_humidity_outside_formatted': current_humidity_outside_formatted,
		'current_temperature_inside_formatted': current_temperature_inside_formatted,
		'current_pressure_formatted': current_pressure_formatted,
		'rain_today_formatted': rain_today_formatted,
	}
	return render(request, 'index.html', context) 

def am2315_maxts():
	cursor = connections['am2315'].cursor()
	cursor.execute('select max(ts) from am2315')
	row = cursor.fetchone()

	return row

def am2315_temp_humidty():
	cursor = connections['am2315'].cursor()
	cursor.execute('select (temperature * 1.8 + 32), humidity from am2315 where ts=\'" + am23125_maxts + "\'")')
	temp, humidity = cursor.fetchone()

	return temp, humidity
	
