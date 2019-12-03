import os
import subprocess
import sys
import csv
import pandas as pd
import altair as alt

silence = []
speech = []

def calc(filePath, start, end, what):
   pass 

# takes a .txt label file (generated from audacity) and turns into a csv for processing
def turnLabelsToDataFrame(path):
    txt_file = path
    #csv_file = path[:-4]+".csv"

    df = pd.read_csv(open(txt_file, "r"), sep = '\t', names=["to", "from", "label"], index_col=False)
    # df.to_csv(csv_file)

    return df

# this classification keeps the noise / cross overs
def classify(labels, winStart, winEnd):

    #TODO: possible optimization: keep track of where we left off? and for loop from there?
    affiliated = []

    for indexSol, rowSol in labels.iterrows():
        labStart = rowSol['to']
        labEnd = rowSol['from']
        lab = rowSol['label']

        if(winStart <= labEnd and labStart <= winEnd):
            entry = {"start": labStart,
                        "end": labEnd,
                        "label": lab}
            affiliated.append(entry)
        
        if(winEnd <= labStart):
            break

    maxPercent = 0.0
    maxPercentsLabel = ""
    for entry in affiliated:
        a = winStart
        b = winEnd
        x = entry["start"]
        y = entry["end"]
        l = entry["label"]

        percent = 0.0
        if(x <= a):
            if(y <= b):
                percent = (y-a)/(b-a)
            else:
                percent = 1.0

        else:
            if(y <= b):
                percent =(y-x)/(b-a)
            else:
                percent = (b-x)/(b-a)

        if(percent > maxPercent): #update!
            maxPercent = percent
            maxPercentsLabel = l
        
    return maxPercentsLabel[:-1]

# this classification keeps the noise / cross overs
def classify_dump_crossovers(labels, winStart, winEnd):
    for indexSol, rowSol in labels.iterrows():
        labStart = float(rowSol['to'])
        labEnd = float(rowSol['from'])
        lab = rowSol['label']

        if(labStart <= winStart and winEnd <= labEnd):
            return lab[0:1]
        
        if(winEnd <= labStart):
            return "DUMPED"

def calcMaxPeakValues(path, windowSize):
    windowFrameSize = int(windowSize)
    if (os.path.isdir(path) == False):
        if path.endswith(".wav"):
            # Generate the csv with the data
            stringCommand="ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=" + str(windowFrameSize) + " -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.Peak_level, -of csv=p=0 -print_format csv>"+path[:-4]+".csv"
            subprocess.call(stringCommand, shell=True)

            df = pd.read_csv(path[:-4]+".csv", header=None)
            maxPeakLevels = df[2].values.tolist()

            result = []
            for i in range (len(maxPeakLevels)):
                if (i % windowFrameSize == windowFrameSize-1 or i == len(maxPeakLevels)-1):
                    result.append(abs(float(maxPeakLevels[i])))

            print(result)
            return result
    return []

def findValForEachSeg(labels, path, metric, intervalLen, destCSV):
    stringCommand="ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=" + str(intervalLen) + " -show_entries frame=pkt_pts_time -of csv=p=0 -print_format csv>"+path[:-4]+".csv"
    subprocess.call(stringCommand, shell=True)

    ampValues = calcMaxPeakValues(path, intervalLen)

    df = pd.read_csv(path[:-4]+".csv", header=None)
    df.rename(columns={0: 'frame', 1: 'time', 2: 'amps'}, inplace=True)
    for i in range(len(df)):
        df.at[i , "frame"]= str(i)
        df.at[i , "amps"]= ampValues[i // int(intervalLen)]

    df = df.iloc[int(intervalLen)::int(intervalLen)] # starting from row 1, takes every other (intervalLen) row
    
    labelClassification = []

    df.to_csv(path[:-4]+".csv", index=False)
    # classify each of the window to a label? 
    winStart = 0
    for index, row in df.iterrows():
        winEnd = float(row['time'])
        totalTime = float(winEnd - winStart)

        if(winStart > 60*18):
            labelClassification.append("UNDEFINED")
        else:
            labelClassification.append(classify_dump_crossovers(labels, winStart, winEnd))
                
        winStart = winEnd

    df.insert(1, "Label", labelClassification, True)

    # Save as csv	
    df.to_csv(destCSV, index=False)

def drawBoxPlot(pathToCSV):
    df = pd.read_csv(pathToCSV)
    # print(df.to_string());  
    # df = df[df.Label != "A"| df.Label != "D"]


    toDrop = df[ (df['Label'] != "A") & (df['Label'] != "D") & (df['Label'] != "S")].index
 
    df.drop(toDrop , inplace=True)

    source = df
    peak = alt.Chart(data=source, height=400, width=200).mark_boxplot(size=40).encode(
        x='Label',
        y='amps'
    )

    alt.hconcat(peak).save('chart.png', scale_factor=2.0)


# argv[1] = .wav file
# argv[2] = .csv labels file
# argv[3] = how many frame rate until resize
# argv[4] = .csv file to store all the audio values
labels = turnLabelsToDataFrame(sys.argv[2]) # this is a dataframe
findValForEachSeg(labels, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
drawBoxPlot(sys.argv[4])
