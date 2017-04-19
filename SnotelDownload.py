#!/data/apps/enthought_python/2.7.3/bin/python

import pandas as pd
from datetime import datetime
from urllib2 import urlopen


def SnotelDownload(yyyy0,mm0,dd0,yyyy1,mm1,dd1):
	start_date=datetime(yyyy0,mm0,dd0).strftime("%Y-%m-%d")
	end_date=datetime(yyyy1,mm1,dd1).strftime("%Y-%m-%d")
	snotel_path="https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customMultipleStationReport/daily/start_of_period/element=%22SNWD%22%20AND%20outServiceDate=%222100-01-01%22%7Cname/"+start_date+","+end_date+"/name,stationId,latitude,longitude,SNWD::value"
	content = urlopen(snotel_path).readlines()
	snotel_line_1 = 'Date,Station Name,Station Id,Latitude,Longitude,Snow Depth (in) Start of Day Values'
	head_idx = [i for i,x in enumerate(content) if snotel_line_1 in x][0]
	list_stations_data = content[head_idx+1:]
	station_dates = []
	station_names = []
	station_ids = []
	station_lats = []
	station_lons = []
	station_snow_depth = []
	for data in list_stations_data:
		tt1 = data.split('\n')[0]
		station_dates.append(tt1.split(',')[0])
		station_names.append(tt1.split(',')[1])
		station_ids.append(tt1.split(',')[2])
		station_lats.append(tt1.split(',')[3])
		station_lons.append(tt1.split(',')[4])
		try:
			station_snow_depth.append(float(tt1.split(',')[5]))
		except:
			station_snow_depth.append(0)
	station_data = pd.DataFrame()
	station_data['Date time'] = station_dates
	station_data['Station name'] = station_names
	station_data['ID'] = station_ids
	station_data['Lat'] = station_lats
	station_data['Lon'] = station_lons
	station_data['SNWD'] = station_snow_depth
#	station_metadata = pd.read_csv('data/nwcc_inventory.csv')
	return station_data

