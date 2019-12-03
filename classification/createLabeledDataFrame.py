import os
import subprocess
import sys
import csv
import pandas as pd

# takes a .txt label file (generated from audacity) and turns into a dataframe for processing
def turnLabelsToDataFrame(path):
    txt_file = path
    dataFrame = pd.read_csv(open(txt_file, "r"), sep = '\t', names=["To", "From", "Label"], index_col=False)
    for i in range(len(dataFrame)):
        old = dataFrame.at[i, "Label"]
        dataFrame.at[i, "Label"] = old[:1]
    return dataFrame


# create series of clips for each label range
def parseClips(dataFrame, audio):
    if (not os.path.isdir("clips/")):
        os.mkdir("clips/")

    for i in range(len(dataFrame)):
        start = dataFrame.at[i, "to"]
        length = dataFrame.at[i, "from"] - start
        stringCommand = "ffmpeg -i " + audio + " -ss " + str(start) + " -t " + str(length) + " clips/clip"+str(i)+".wav"
        subprocess.call(stringCommand, shell=True)

# create csvs of three stats for each clip, sampled at rate of 1 frame
def createClipValues():
    if (not os.path.isdir("csvs/")):
        os.mkdir("csvs/")

    for i in range(len(dataFrame)):
        path = "clips/clip"+str(i)+".wav"
        csvPath = "csvs/clip"+str(i)+".csv"
        stringCommand="ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=1 -show_entries frame_tags=lavfi.astats.Overall.Peak_level,lavfi.astats.Overall.RMS_peak,lavfi.astats.Overall.RMS_level, -of csv=p=0 -print_format csv>"+csvPath
        subprocess.call(stringCommand, shell=True)


def augmentValues(dataFrame):
    dataFrame["Overall Peak"] = ""
    dataFrame["Overall RMS Peak"] = ""
    dataFrame["Overall RMS Level"] = ""
    
    for i in range(len(dataFrame)):
        path = "csvs/clip"+str(i)+".csv"
        allValues = pd.read_csv(open(path, "r"), sep = ',', names=["Frame", "Overall Peak", "Overall RMS Peak", "Overall RMS Level"], index_col=False)
        
        dataFrame.at[i, "Overall Peak"] = allValues["Overall Peak"].mean()
        dataFrame.at[i, "Overall RMS Peak"] = allValues["Overall RMS Peak"].mean()
        dataFrame.at[i, "Overall RMS Level"] = allValues["Overall RMS Level"].mean()

    dataFrame = dataFrame.drop(["To", "From"], axis=1)
    
    csvPath = "labeledValues.csv"
    dataFrame.to_csv(csvPath, index=False)
        



# argv[1] = .txt labels file
dataFrame = turnLabelsToDataFrame(sys.argv[1])

# consider adding another argument so that parseClips and createClipValues aren't run every time
# argv[2] = .wav file
#parseClips(dataFrame, sys.argv[2])
#createClipValues()

augmentValues(dataFrame)