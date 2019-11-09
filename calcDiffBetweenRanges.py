import os
import subprocess
import sys
import csv
import pandas as pd
silence = []
speech = []

def calc(filePath, start, end, what):
   pass 

def turnLabelsToCSV(path):
    txt_file = path
    csv_file = path[:-4]+".csv"

    df = pd.read_csv(open(txt_file, "r"), sep = '\t', names=["to", "from", "label"], index_col=False)
    df.to_csv(csv_file)

    return df

def findValForEachSeg(labels, path):

    overallDF = pd.DataFrame(columns=['label', 'variance'])

    txt_file = r"log.txt"
    csv_file = r"mycsv.csv"

    for index, row in labels.iterrows():
        
        start = row['to']
        end = row['from']
        lab = row['label']
        
        getDataCommand = "ffmpeg -hide_banner -loglevel panic -ss "+str(start)+" -to " + str(end) + " -i " + path+ " -af astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=log.txt -f null -"
        subprocess.call(getDataCommand, shell=True)
        
        # df for this one section
        df = pd.read_csv(open(txt_file, "r"), sep ='frame:|pts:|pts_time:|lavfi.astats.Overall.RMS_level=|\n', header=None, index_col=False, engine='python')
        df = df.iloc[1::2] # starting from row 1, delete every other row
        df = df.iloc[:, 1:2] # take the RMS Level column
        df.index = ["frame " + str(i) for i in range (df.size)]
        df.columns = ["RMS_Level"]

        variance = df.var()['RMS_Level']
        overallDF = overallDF.append({'label':lab[:1], 'variance':variance}, ignore_index=True)
        
        
    overallDF.to_csv(csv_file)

    silenceSum = 0
    silenceCount = 0

    davidSum = 0
    davidCount = 0

    amySum = 0
    amyCount = 0

    for index, row in overallDF.iterrows():
        lab = row['label']
        variance = row['variance']

        if(lab == 'S'):
            silenceSum += variance
            silenceCount += 1
        elif(lab == 'D'):
            davidSum += variance
            davidCount += 1
        elif(lab == 'A'):
            amySum += variance
            amyCount += 1
    
    print("Silence's average variance: " + str(silenceSum/silenceCount))
    print("David's average variance: " + str(davidSum/davidCount))
    print("Amy's average variance: " + str(amySum/amyCount))





def calcDiffBetweenRanges(audio, label, whatData):
    pass

# argv[1] = .wav file
# argv[2] = .csv labels file
# argv[3] = what data are we finding variance for
labels = turnLabelsToCSV(sys.argv[2]) # this is a dataframe
findValForEachSeg(labels, sys.argv[1])
calcDiffBetweenRanges(sys.argv[1], sys.argv[2], sys.argv[3])