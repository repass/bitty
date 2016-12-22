#!/usr/bin/python3
# repass 10/28/15 create some weather graphs on plotly

import sqlite3

import datetime
import plotly.plotly as py
import plotly.graph_objs as go

con = sqlite3.connect('/home/repass/db/am2315.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
with con:
	con.row_factory = sqlite3.Row
	c = con.cursor()

	outside_timestamp=[]
	outside_humidity=[]
	outside_temperature=[]
	outside_timestamp_this_week=[]
	outside_humidity_this_week=[]
	outside_temperature_this_week=[]
	plotdata=[]
	c.execute("select ts, (temperature * 1.8 + 32), humidity from am2315 where ts > (datetime(\'now\',\'localtime\','start of day\'))")
	rows = c.fetchall()
	for myrow in rows:
		outside_timestamp.append(myrow[0])
		outside_temperature.append(myrow[1])
		outside_humidity.append(myrow[2])

#	c.execute("select ts, (temperature * 1.8 + 32), humidity from am2315 where ts > (datetime(\'now\',\'localtime\','start of week\'))")
#	for myrow in rows:
#		outside_timestamp_this_week.append(myrow[0])
#		outside_temperature_this_week.append(myrow[1])
#		outside_humidity_this_week.append(myrow[2])

#	c.execute("select strftime('%s','now','start of day'), strftime('%s',max(ts)) from am2315")
#	start_time,end_time = c.fetchone()
#	print ("Start time: " ,start_time," End time: ", end_time)
	
con.close()

con = sqlite3.connect('/home/repass/db/bmp180.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
with con:
	con.row_factory = sqlite3.Row
	c = con.cursor()

	inside_timestamp=[]
	pressure=[]
	inside_temperature=[]
	inside_timestamp_this_week=[]
	pressure_this_week=[]
	inside_temperature_this_week=[]
	plotdata=[]
	c.execute("select ts, (temperature * 1.8 + 32), pressure from bmp180 where ts > (datetime(\'now\',\'localtime\','start of day\'))")
	rows = c.fetchall()
	for myrow in rows:
		inside_timestamp.append(myrow[0])
		inside_temperature.append(myrow[1])
		pressure.append(myrow[2])
	
#	c.execute("select ts, (temperature * 1.8 + 32), pressure from bmp180 where ts > (datetime(\'now\',\'localtime\','start of week\'))")
#	rows = c.fetchall()
#	for myrow in rows:
#		inside_timestamp_this_week.append(myrow[0])
#		inside_temperature_this_week.append(myrow[1])
#		pressure_this_week.append(myrow[2])
	
con.close()

con = sqlite3.connect('/home/repass/db/gpio.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
with con:
	con.row_factory = sqlite3.Row
	c = con.cursor()

	io_timestamp=[]
	rainfall=[]
	windspeed=[]
	plotdata=[]
	day_dict = dict()
	c.execute("select distinct(date(ts)) from io where ts > date(\'now\',\'-14 days\')group by date(ts)")
	rows = c.fetchall()
	for myrow in rows:
		day_dict[myrow[0]]=0;

	c.execute("select distinct(date(ts)), (count(ts) *0.011) from io where port=13 and ts > date(\'now\',\'-14 days\')group by date(ts)")
	rows = c.fetchall()
	for myrow in rows:
#		io_timestamp.append(myrow[0])
#		rainfall.append(myrow[1])
		day_dict[myrow[0]]=myrow[1]
	
con.close()

for mykey in day_dict.keys():
	io_timestamp.append(mykey)
	rainfall.append(day_dict[mykey])
	

outside_temperature_trace = go.Scatter(
		x=outside_timestamp,
		y=outside_temperature,
		name='Outside Temperature',
		yaxis='y0',
		line=dict(
			color='rgb(44,160,44)'
			)
		)

#outside_temperature_trace_this_week = go.Scatter(
#		x=outside_timestamp_this_week,
#		y=outside_temperature_this_week,
#		name='Outside Temperature',
#		yaxis='y0',
#		line=dict(
#			color='rgb(44,160,44)'
#			)
#		)
#
inside_temperature_trace = go.Scatter(
		x=inside_timestamp,
		y=inside_temperature,
		name='Inside Temperature',
		yaxis='y0',
		line=dict(
			color='rgb(106,168,79)'
			)
		)

#inside_temperature_trace_this_week = go.Scatter(
#		x=inside_timestamp_this_week,
#		y=inside_temperature_this_week,
#		name='Inside Temperature',
#		yaxis='y0',
#		line=dict(
#			color='rgb(106,168,79)'
#			)
#		)

#outside_humidity_trace_this_week = go.Scatter(
#		x=outside_timestamp_this_week,
#		y=outside_humidity_this_week,
#		name='Outside Humidity',
#		yaxis='y1',
#		line=dict(
#			color='rgb(31,119,180)'
#			)
#
##		)

outside_humidity_trace = go.Scatter(
		x=outside_timestamp,
		y=outside_humidity,
		name='Outside Humidity',
		yaxis='y1',
		line=dict(
			color='rgb(31,119,180)'
			)

		)

pressure_trace = go.Scatter(
		x=inside_timestamp,
		y=pressure,
		name='Atmospheric Pressure',
		yaxis='y2',
		line=dict(
			color='rgb(166,77,121)'
			)
		)

rainfall_trace = go.Bar(
		x=io_timestamp,
		y=rainfall,
		name='Rainfall'
		)

layout = go.Layout(
	title='Temperature Today',
	xaxis=dict(
		title='Time',
	),
	yaxis=dict(
		title='Temperature F',
		)
	)
data = [outside_temperature_trace, inside_temperature_trace]
fig = go.Figure(data=data, layout=layout)
plot_url=py.plot(fig,filename='temperature-today')

#layout = go.Layout(
#	title='Temperature This Week',
#	xaxis=dict(
#		title='Time',
#	),
#	yaxis=dict(
#		title='Temperature F',
#		)
#	)
#data = [outside_temperature_trace_this_week, inside_temperature_trace_this_week]
#fig = go.Figure(data=data, layout=layout)
#plot_url=py.plot(fig,filename='temperature-this-week')

#layout = go.Layout(
#	title='Humidity Today',
#	xaxis=dict(
#		title='Time',
#	),
#	yaxis=dict(
#		title='Relative Humidity %',
#		)
#	)
#data = [outside_humidity_trace]
#fig = go.Figure(data=data, layout=layout)
#plot_url=py.plot(fig,filename='humidity-today')

#layout = go.Layout(
#	title='Atmospheric Pressure Today',
#	xaxis=dict(
#		title='Time',
#	),
#	yaxis=dict(
#		title='Pressure Pa',
#		)
#	)
#data = [pressure_trace]
#fig = go.Figure(data=data, layout=layout)
#plot_url=py.plot(fig,filename='pressure-today')

layout = go.Layout(
	title='Rainfall Previous Two Weeks',
	xaxis=dict(
		title='Time',
	),
	yaxis=dict(
		title='Inches Rain',
		)
	)
data = [rainfall_trace]
fig = go.Figure(data=data, layout=layout)
plot_url=py.plot(fig,filename='rainfall-twoweeks')

#############
layout = go.Layout(
	title='Weather Today',
	xaxis=dict(
		title='Time',
	),
	yaxis=dict(
		title='Outside Humidity RH%',
		),
	yaxis2=dict(
		title='Atmospheric Pressure Pa',
		overlaying='y',
		side='right'
		),
	yaxis3=dict(
		title='Outside Temperature',
		overlaying='y',
		side='left',
		position=0.15
		)
	)
data = [outside_humidity_trace,pressure_trace,outside_temperature_trace]
fig = go.Figure(data=data, layout=layout)
plot_url=py.plot(fig,filename='weather-today')

#print("Finished updating static plotly")
