#!/usr/bin/python
#repass 10/23/15 create a graph from sqlite data

import pandas as pd
import numpy as np
from pandas import Series, DataFrame, Panel
import sqlite3

con = sqlite3.connect('/home/repass/db/weather.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

c = con.cursor()

#for row in c.execute('select * from am2315'):
#	print row
rows = c.fetchall()

ROWSeries = Series(rows[:2], index=rows[:0])

ROWSeries.plot()
ROWSeries.savefig("am1235.png")

con.close()



