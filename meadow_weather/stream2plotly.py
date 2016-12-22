#!/usr/bin/python3
#repass 10/23/15 monitor sqlite tables and upload changes to plotly


import sqlite3

import time
import datetime
import plotly.plotly as py
#import plotly.graph_objs as go
from plotly.graph_objs import *

con = sqlite3.connect('/home/repass/db/plotly.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

outdoor_temperature_trace = Scatter(
	x=[],
	y=[],
	name='Outdoor Temperature',
	yaxis='y0',
	stream=dict(token='8qgc0vdodr', maxpoints=2880)
	)

indoor_temperature_trace = Scatter(
	x=[],
	y=[],
	name='Indoor Temperature',
	yaxis='y0',
	stream=dict(token='y8q7ej8mfx',maxpoints=2880)
	)

data = Data([outdoor_temperature_trace,indoor_temperature_trace])
layout = Layout(
	title='Temperature',
	xaxis=dict(
		title='Time',
		),
	yaxis=dict(
		title='Temperature F'
		)
	)

fig=Figure(data=data, layout=layout)
unique_url = py.plot(fig,filename='temperature-stream', fileopts='extend')
#unique_url = py.plot(fig,filename='temperature-stream')

outdoor_temperature_stream = py.Stream('8qgc0vdodr')
outdoor_temperature_stream.open()

indoor_temperature_stream = py.Stream('y8q7ej8mfx')
indoor_temperature_stream.open()

outdoor_humidity_trace = Scatter(
	x=[],
	y=[],
	name='Outdoor Humidity',
	yaxis='y1',
	stream=dict(token='tw0jdhe5hl', maxpoints=2880)
	)

data = Data([outdoor_humidity_trace])
humidity_layout = Layout(
	title='Humidity',
	xaxis=dict(
		title='Time',
		),
	yaxis=dict(
		title='Relative Humidity %'
		)
	)

humidity_fig=Figure(data=data, layout=humidity_layout)
humidity_url = py.plot(humidity_fig,filename='humidity-stream', fileopts='extend')
#humidity_url = py.plot(humidity_fig,filename='humidity-stream')

outdoor_humidity_stream = py.Stream('tw0jdhe5hl')
outdoor_humidity_stream.open()
#########

pressure_trace = Scatter(
	x=[],
	y=[],
	name='Atmospheric Pressure',
	yaxis='y2',
	stream=dict(token='o652oe47c9', maxpoints=2880)
	)

data = Data([pressure_trace])
pressure_layout = Layout(
	title='Atmospheric Pressure',
	xaxis=dict(
		title='Time',
		),
	yaxis=dict(
		title='Pressure Pa'
		)
	)

pressure_fig=Figure(data=data, layout=pressure_layout)
pressure_url = py.plot(pressure_fig,filename='pressure-stream', fileopts='extend')
#pressure_url = py.plot(pressure_fig,filename='pressure-stream')

pressure_stream = py.Stream('o652oe47c9')
pressure_stream.open()
###########
data = Data([outdoor_temperature_trace,outdoor_humidity_trace,pressure_trace])
combined_layout = Layout(
	title='Streaming Weather',
	xaxis=dict(
		title='Time',
		),
	yaxis=dict(
		title='Temperature F'
		),
	yaxis1=dict(
		title='Humidity %RH',
		anchor='free',
		overlaying='y',
		side='left',
		position=0.15
		),
	yaxis2=dict(
		title='Pressure Pa',
		anchor='x',
		overlaying='y',
		side='right'
		),
	)

combined_fig=Figure(data=data, layout=combined_layout)
combined_url = py.plot(combined_fig,filename='weather-stream', fileopts='extend')
##combined_url = py.plot(combined_fig,filename='weather-stream')


############
am2315_con = sqlite3.connect('/home/repass/db/am2315.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

bmp180_con = sqlite3.connect('/home/repass/db/bmp180.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

with con:
	con.row_factory = sqlite3.Row
	c = con.cursor()

	while True:
		c.execute("select max(ts) from am2315");
		maxts_am2315=c.fetchone();
#		print(maxts_am2315[0])
		maxtsam2315=maxts_am2315[0]
		#print(maxtsam2315)

		with am2315_con:
			am2315_con.row_factory = sqlite3.Row
			am2315_c = am2315_con.cursor()
#			print("maxtsam2315 is ",maxtsam2315)
			am2315_c.execute("select ts from am2315 where ts > ?", [maxtsam2315])
			rows=am2315_c.fetchall()
			for row in rows:
#				print("Preparing to enqueue " ,row[0])
				c.execute("insert into am2315(ts) values (?)",[row[0]])
				
			con.commit()
		
			c.execute("select max(ts) from am2315")
			newmaxts=c.fetchone()[0]
			c.execute("select ts from am2315 where ts < ?",[newmaxts])
			stream_ts_rows=c.fetchall()
			for stream_ts_row in stream_ts_rows:
				stream_ts=stream_ts_row[0]
				am2315_c.execute("select (temperature * 1.8 + 32), humidity from am2315 where ts = ?",[stream_ts])
				stream_temp,stream_humidity=am2315_c.fetchone()
#				print("Preparing to upload am2315 x=", stream_ts, ' y=',stream_temp)
				outdoor_temperature_stream.write(dict(x=stream_ts,y=stream_temp))
				outdoor_humidity_stream.write(dict(x=stream_ts,y=stream_humidity))
				c.execute("delete from am2315 where ts = ?",[stream_ts])
				time.sleep(0.03)	
			con.commit()

		c.execute("select max(ts) from bmp180");
		maxts_bmp180=c.fetchone();
		maxts_bmp180=maxts_bmp180[0]

		with bmp180_con:
			bmp180_con.row_factory = sqlite3.Row
			bmp180_c = bmp180_con.cursor()
			bmp180_c.execute("select ts from bmp180 where ts > ?", [maxts_bmp180])
			rows=bmp180_c.fetchall()
			for row in rows:
#				print("Preparing to enqueue " ,row[0])
				c.execute("insert into bmp180(ts) values (?)",[row[0]])
				
		
			c.execute("select max(ts) from bmp180")
			newmaxts=c.fetchone()[0]
			c.execute("select ts from bmp180 where ts < ?",[newmaxts])
#			print("New maximum ts for bmp180 is: ",[newmaxts])
			stream_ts_rows=c.fetchall()
			for stream_ts_row in stream_ts_rows:
				bmp180_stream_ts=stream_ts_row[0]
				bmp180_c.execute("select (temperature * 1.8 + 32), pressure from bmp180 where ts = ?",[bmp180_stream_ts])
				stream_temp_inside,stream_pressure=bmp180_c.fetchone()
#				print("Preparing to upload bmp180 x=", bmp180_stream_ts, ' y=',stream_temp_inside)
				indoor_temperature_stream.write(dict(x=bmp180_stream_ts,y=stream_temp_inside))
				pressure_stream.write(dict(x=bmp180_stream_ts,y=stream_pressure))
				c.execute("delete from bmp180 where ts = ?",[bmp180_stream_ts])
				con.commit()
				time.sleep(0.03)	

#			con.commit()
		time.sleep(30)	

am2315_con.close()
bmp180_con.close()
con.close()
outdoor_temperature_stream.close()
indoor_temperature_stream.close()
outdoor_humidity_stream.close()
pressure_stream.close()
