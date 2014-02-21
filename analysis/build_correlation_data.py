# fetch all records for station 54 between the hours of 9 and 10 on weekdays in June
import os
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates
from datetime import date, timedelta
import random
import datetime
from matplotlib.ticker import NullFormatter
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import FixedLocator
from datetime import tzinfo

conn = psycopg2.connect(database='bikeshare',user='bikeshare',host='bikeshare.ctmvy2bluoic.us-west-2.rds.amazonaws.com',password="bikeshare")

cur = conn.cursor()

cur.execute("SELECT id, name FROM metadata_washingtondc;")
stations = list(cur.fetchall())
#stations = list(stations[i] for i in [17,128,52,104])
stations = list(stations[i] for i in [52,104])

# extract data for station where tfl_id = 54
cur.execute("select * from bike_ind_washingtondc where tfl_id = 54 AND date_part('month',timestamp) = 6 AND date_part('hour',timestamp) >= 13 AND date_part('hour',timestamp) < 14 AND extract(dow from timestamp) > 0 AND  extract(dow from timestamp) < 6;")
station_54 = cur.fetchall()
station_54_df = pd.DataFrame.from_records(station_54, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = ["timestamp"])
timezone = 'US/Eastern'
station_54_df.index = station_54_df.index.tz_localize('UTC').tz_convert(timezone) 
station_54_df = station_54_df.resample("2MIN")
station_54_df.to_csv('station_54_june.csv', sep=',')

cur.execute("select * from bike_ind_washingtondc where tfl_id = 106 AND date_part('month',timestamp) = 6 AND date_part('hour',timestamp) >= 13 AND date_part('hour',timestamp) < 14 AND extract(dow from timestamp) > 0 AND  extract(dow from timestamp) < 6;")
station_106 = cur.fetchall()
station_106_df = pd.DataFrame.from_records(station_106, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = ["timestamp"])
timezone = 'US/Eastern'
station_106_df.index = station_106_df.index.tz_localize('UTC').tz_convert(timezone) 
station_106_df = station_106_df.resample("2MIN")
station_106_df.to_csv('station_106_june.csv', sep=',')

cur.execute("select * from bike_ind_washingtondc where tfl_id = 10 AND date_part('month',timestamp) = 6 AND date_part('hour',timestamp) >= 13 AND date_part('hour',timestamp) < 14 AND extract(dow from timestamp) > 0 AND  extract(dow from timestamp) < 6;")
station_10 = cur.fetchall()
station_10_df = pd.DataFrame.from_records(station_10, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = ["timestamp"])
timezone = 'US/Eastern'
station_10_df.index = station_10_df.index.tz_localize('UTC').tz_convert(timezone) 
station_10_df = station_10_df.resample("2MIN")
station_10_df.to_csv('station_10_june.csv', sep=',')


temp_54 = station_54_df.dropna(axis=0)
temp_54 = rebalance_station_poisson_data(temp_54, 54, '30MIN', include_rebalance = False)
delta_54 = temp_54.ix[(temp_54['months'] == 6) & (temp_54['hours'] == 9) & (temp_54['weekday_dummy'] == 1),:]
corr_54 = delta_54['arrivals']
corr_54.to_csv('corr_54.csv', sep = ',')

temp_106 = station_106_df.dropna(axis=0)
temp_106 = rebalance_station_poisson_data(temp_106, 106, '30MIN', include_rebalance = False)
delta_106 = temp_106.ix[(temp_106['months'] == 6) & (temp_106['hours'] == 9) & (temp_106['weekday_dummy'] == 1),:]
corr_106 = delta_106['arrivals']
corr_106.to_csv('corr_106.csv', sep = ',')

temp_10 = station_10_df.dropna(axis=0)
temp_10 = rebalance_station_poisson_data(temp_10, 10, '30MIN', include_rebalance = False)
delta_10 = temp_10.ix[(temp_10['months'] == 6) & (temp_10['hours'] == 9) & (temp_10['weekday_dummy'] == 1),:]
corr_10 = delta_10['arrivals']
corr_10.to_csv('corr_10.csv', sep = ',')