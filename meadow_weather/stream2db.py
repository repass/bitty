#!/usr/bin/python3
#repass 10/23/15 monitor sqlite tables and upload changes to plotly
#repass 4/7/16 modify to stream to db


import sqlite3

import time
import datetime
import plotly.plotly as py
#import plotly.graph_objs as go
#from plotly.graph_objs import *

import psycopg2


con = sqlite3.connect('/home/repass/db/stream2db.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

try:
	pgcon = psycopg2.connect("dbname=weather user=weather host=hope password=ritchie")
except:
	quit()

pgcon.autocommit = True

pgcur = pgcon.cursor()

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
				###outdoor_temperature_stream.write(dict(x=stream_ts,y=stream_temp))
				###outdoor_humidity_stream.write(dict(x=stream_ts,y=stream_humidity))
				pgcur.execute("insert into am2315 (ts, temperature, humidity) values (%s, %s, %s)",(stream_ts, stream_temp, stream_humidity))
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
				###indoor_temperature_stream.write(dict(x=bmp180_stream_ts,y=stream_temp_inside))
				###pressure_stream.write(dict(x=bmp180_stream_ts,y=stream_pressure))
				pgcur.execute("insert into bmp180 (ts, temperature, pressure) values (%s, %s, %s)", (bmp180_stream_ts, stream_temp_inside, stream_pressure))
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
