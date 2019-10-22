import altair as alt
import numpy as np
import pandas as pd

import os
import subprocess
import sys
import csv


def generateMatrixFromWav(path):
	if (os.path.isdir(path) == False):
		if path.endswith(".wav"):
            # convert into csv, maybe create a new folder?
			# the reset paramter 48 is achieved through 48000/1000 as adivsed by 
			# https://superuser.com/questions/1183663/determining-audio-level-peaks-with-ffmpeg
			blehstringCommand="ffmpeg -i "+path+" -af astats=metadata=1:reset=48000, ametadata=print:key=lavfi.astats.Overall.RMS_level:file=log.txt -f null -"

			cpCommand = "ffmpeg -i "+path+" -af astats=metadata=1:reset=486,ametadata=print:key=lavfi.astats.Overall.RMS_level:file="+path[:-4]+".csv -f null -"
			
			oldC = "ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=486:length=1 -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.RMS_level, -of csv=p=0 -print_format csv>"+path[:-4]+".csv"

# ffmpeg -i in.mp3 -af astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=log.txt -f null -

			stringCommand="ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=7040 -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.Peak_level,lavfi.astats.Overall.RMS_peak,lavfi.astats.Overall.Flat_factor,lavfi.astats.Overall.Peak_count,lavfi.astats.Overall.Dynamic_range, -of csv=p=0 -print_format csv>"+path[:-4]+".csv"

			subprocess.call(blehstringCommand, shell=True)

            # call rscript to combine the csvs into a matrix

            # delete all the extra csv

	else:
		for filename in os.listdir(path):
			generateMatrixFromWav(path + "/" + filename)

# To be written after we get a proper format csv data file
# def generateHeatMap():

def generateCombinedCSV(path):
	counter = 0
	with open(path+"/matrix.csv", 'a') as res:
		writer = csv.writer(res)
		writer.writerow(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])
	res = pd.read_csv(path+"/matrix.csv")
	generateCombinedCSVhelper(path, res, counter)

def generateCombinedCSVhelper(path, res, counter):
	if (os.path.isdir(path) == False):
		if path.endswith(".csv"):
			counter += 1
			csv_input = pd.read_csv(path)	
			res[str(counter)] = csv_input[2]

	else:
		for filename in os.listdir(path):
			generateCombinedCSVhelper(path + "/" + filename, res, counter)

#     # Compute x^2 + y^2 across a 2D grid
#     x, y = np.meshgrid(range(-5, 5), range(-5, 5))
#     z = x ** 2 + y ** 2

#     # Convert this grid to columnar data expected by Altair
#     source = pd.DataFrame({'x': x.ravel(),
#                         'y': y.ravel(),
#                         'z': z.ravel()})

#     alt.Chart(source).mark_rect().encode(
#         x='x:O',
#         y='y:O',
#         color='z:Q'
#     ).save('chart.jpg')

generateMatrixFromWav(sys.argv[1])