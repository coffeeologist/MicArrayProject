import altair as alt
import numpy as np
import pandas as pd

import os
import subprocess
import sys
import csv
import copy


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

def heatMap(path):
    # Compute x^2 + y^2 across a 2D grid
    sourceCSV = pd.read_csv(path)

    for n in range (0, sourceCSV.shape[0]):

        snapShot = sourceCSV.iloc[n, 1:]

        x, y = np.meshgrid(range(0, 23), range(0, 4))

        # Currently assumed format of the charts:
        #  12 11 10
        #   9  8  7
        #   6  5  4
        #   3  2  1
        convertedX = copy.deepcopy(x)
        for i in range (len(x)):
            for j in range (len(x[0])):
                if(x[i][j] <= 6):
                    convertedX[i][j] = 0
                elif( 7 <= x[i][j] <= 15):
                    convertedX[i][j] = 1
                else:
                    convertedX[i][j] = 2
        z = snapShot[12-(3*y+1)-1]
        for i in range (len(convertedX)):
            for j in range (len(convertedX[0])):
                z[i][j] = snapShot[12 - ( 3*(y[i][j]) + (convertedX[i][j])) - 1] 

        # Convert this grid to columnar data expected by Altair
        source = pd.DataFrame({'x': x.ravel(),
                            'y': y.ravel(),
                            'z': z.ravel()})

        # TODO: possibly make the size arguments an optional commandline argument? 
        resChart = alt.Chart(data=source, height=400, width=600).mark_rect(strokeWidth=100).encode(
            x='x:O',
            y='y:O',
            color='z:Q').configure_axis(labelFontSize=10).configure_scale(barBandPaddingInner=0, bandPaddingInner=0, bandPaddingOuter=0).save('chart' + str(n) + '.png')

heatMap(sys.argv[1])
# generateMatrixFromWav(sys.argv[1])