#!/usr/bin/python
#repass 10/26/15 print a weather summary

import sqlite3

import datetime
import random
import matplotlib.pyplot as plt
#import plotly.plotly as py
#import plotly.graph_objs as go

con = sqlite3.connect('/home/repass/db/gpio.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
with con:
	con.row_factory = sqlite3.Row
	c = con.cursor()

	c.execute('select date(max(ts)) from io')
	lastday_gpio=c.fetchone()
	selectstr="select (count(ts) * 0.011) from io where port = 13 and date(ts) = \'" + lastday_gpio[0] + "\'"
	c.execute(selectstr)
	rain_today=c.fetchone()
	print "Rainfall today: %s inches" % (format(rain_today[0], '.3f'))

# maximum windspeed last hour
	#selectstr="select (1.492 / min(delta)) from io where port=5 and ts > (select datetime(julianday(\'now\',\'localtime\') - .0416666))"
#	#print selectstr
	#c.execute(selectstr)
	#last_hour_max_speed =c.fetchone()
	#print "Maximum windspeed last hour: %sMPH" % (format(last_hour_max_speed[0],'.1f') )

# maximum windspeed today
	selectstr="select (1.492 / min(delta)) from io where port=5 and ts > (select datetime(\'now\',\'localtime\','start of day\'))"
#	print selectstr
	c.execute(selectstr)
	today_max_speed =c.fetchone()
	#print "Maximum windspeed today: %sMPH" % (format(today_max_speed[0],'.1f')) 

#	x=[]
#	y1=[]
#	y2=[]
#	c.execute("select ts,(1.492/delta) from io where port = 5 and ts > (datetime(\'now\',\'localtime\','start of day\'))");
#	rows = c.fetchall()
#	for myrow in rows:
##		print myrow[0], myrow[1]
#		x.append(myrow[0])
#		y1.append(myrow[1])
con.close()
#plt.plot(x,y1)
#plt.legend(['Windspeed Today'])
#plt.gcf().autofmt_xdate()
#plt.show()


con = sqlite3.connect('/home/repass/db/am2315.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
with con:
	con.row_factory = sqlite3.Row
	c = con.cursor()

	c.execute('select max(ts) from am2315')
	maxts_am2315=c.fetchone()
	selectstr="select (temperature * 1.8 + 32), humidity from am2315 where ts=\'" + maxts_am2315[0] + "\'"
	c.execute(selectstr)
	temperature_am2315, humidity_am2315 = c.fetchone()
	print "Outdoor Temperature: %sF Humidity: %s Percent " % (format(temperature_am2315,'.1f'),format(humidity_am2315,'.1f'))
	selectstr="select (min(temperature) * 1.8 + 32), (max(temperature) * 1.8 + 32), min(humidity), max(humidity) from am2315 where ts > (select datetime(\'now\',\'localtime\','start of day\'))"
	c.execute(selectstr)
	min_temp_today,max_temp_today,min_humidity_today,max_humidity_today = c.fetchone()
	print "Minimum/Maximum Temperature today: %sF/%sF Humidity today: %sRH/%sRH" % (format(min_temp_today,'.1f'),format(max_temp_today,'.1f'),format(min_humidity_today,'.1f'),format(max_humidity_today,'.1f'))
#	print selectstr

	xt=[]
	yt1=[]
	yt2=[]
	c.execute("select ts, (temperature * 1.8 + 32), humidity from am2315 where ts > (datetime(\'now\',\'localtime\','start of day\'))");
#	c.execute("select ts, (temperature * 1.8 + 32), humidity from am2315");
	rows = c.fetchall()
	for myrow in rows:
#		print myrow[0], myrow[1]
		xt.append(myrow[0])
		yt1.append(myrow[1])
		yt2.append(myrow[2])
con.close()
#plt.plot(xt,yt1,'k:',label='Outside')
#plt.legend(['Outdoor Temperature'])
#plt.gcf().autofmt_xdate()
#plt.show()

con = sqlite3.connect('/home/repass/db/bmp180.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
with con:
	con.row_factory = sqlite3.Row
	c = con.cursor()

	c.execute('select max(ts) from bmp180')
	maxts_bmp180=c.fetchone()
	selectstr="select (temperature * 1.8 + 32), pressure from bmp180 where ts=\'" + maxts_bmp180[0] + "\'"
	c.execute(selectstr)
	temperature_bmp180, pressure = c.fetchone()
	print "Indoor Temperature: %sF Pressure: %s Pa " % (temperature_bmp180,pressure)

	x=[]
	y1=[]
	y2=[]
	pdata=dict()
	c.execute("select ts, (temperature * 1.8 + 32), pressure from bmp180 where ts > (datetime(\'now\',\'localtime\','start of day\'))");
	rows = c.fetchall()
	for myrow in rows:
#		print myrow[0], myrow[1]
		x.append(myrow[0])
		y1.append(myrow[1])
		y2.append(myrow[2])
		pdata["myrow[0]"]=myrow[1]
con.close()
pdata=(x,y1)
#plt.plot(x,y1,'r--', label='Inside')

#plt.ylabel("Temperature F")

#plt.gcf().autofmt_xdate()
#plt.show()

#import plotly.plotly as py
#import plotly.graph_objs as go
#plot_url = py.plot(pdata,filename='plotly-test')

