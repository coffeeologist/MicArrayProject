import os
import subprocess
import sys
import csv
import pandas as pd
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

def findValForEachSeg(labels, path, metric, intervalLen):
    stringCommand="ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=" + str(intervalLen) + " -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.Peak_level,lavfi.astats.Overall.RMS_peak,lavfi.astats.Overall.RMS_level, -of csv=p=0 -print_format csv>"+path[:-4]+".csv"
    subprocess.call(stringCommand, shell=True)

    df = pd.read_csv(path[:-4]+".csv", header=None)
    df.rename(columns={0: 'frame', 1: 'time', 2: 'Peak Level', 3: 'RMS Peak', 4: 'RMS Level'}, inplace=True)
    for i in range(len(df)):
        df.at[i , "frame"]= str(i)

    df = df.iloc[int(intervalLen)::int(intervalLen)] # starting from row 1, takes every other (intervalLen) row
    
    labelClassification = []

    df.to_csv(path[:-4]+".csv", index=False)
    # classify each of the window to a label? 
    winStart = 0
    for index, row in df.iterrows():
        winEnd = float(row['time'])
        totalTime = float(winEnd - winStart)

        # Due to annotation limitations, we can only go up to 5mins
        if(winStart > 300):
            labelClassification.append("UNDEFINED")
        else:

            #TODO: possible optimization: keep track of where we left off? and for loop from there?
            flag = True
            print("for frame: " + str(row['frame']))
            print("window start time: " + str(winStart) + " | end time: " + str(winEnd))

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
            
            # # Looped till the end and couldn't find anything?
            # if(flag):
            #     labelClassification.append("UNDEFINED")
        

            # treat the list of affiliated; find the majority
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
                
            
            labelClassification.append(maxPercentsLabel)
                
        winStart = winEnd

    print(len(labelClassification))

    df.insert(1, "Label", labelClassification, True)

    # Save as csv	
    df.to_csv(path[:-4]+".csv", index=False)


    # overallDF = pd.DataFrame(columns=['label', 'peak', "RMSPeak", "RMSLevel"])

    # txt_file = r"log.txt"
    # csv_file = r"mycsv.csv"

    # # Loop through each segment/label region 
    # for index, row in labels.iterrows():
        
    #     start = row['to']
    #     end = row['from']
    #     lab = row['label']
        
    #     getDataCommand = "ffmpeg -hide_banner -loglevel panic -ss "+str(start)+" -to " + str(end) + " -i " + path+ " -af astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall." + metric +":file=log.txt -f null -"
    #     subprocess.call(getDataCommand, shell=True)
        
    #     # parse the output data from ffmpeg
    #     df = pd.read_csv(open(txt_file, "r"), sep ='frame:|pts:|pts_time:|lavfi.astats.Overall.' + metric + '=|\n', header=None, index_col=False, engine='python')
    #     df = df.iloc[1::2] # starting from row 1, delete every other row
    #     df = df.iloc[:, 1:2] # take the RMS Level column
    #     df.index = ["frame " + str(i) for i in range (df.size)]
    #     df.columns = [metric]

    #     # calculate variance 
    #     variance = df.var()[metric]
    #     overallDF = overallDF.append({'label':lab[:1], 'variance':variance}, ignore_index=True)
        
    # # export as csv for records    
    # overallDF.to_csv(csv_file)

    # return overallDF

def analyze(overallDF):
    res = {}
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
# argv[4] = how many frame rate until resize
labels = turnLabelsToDataFrame(sys.argv[2]) # this is a dataframe
findValForEachSeg(labels, sys.argv[1], sys.argv[3], sys.argv[4])
#calcDiffBetweenRanges(sys.argv[1], sys.argv[2], sys.argv[3])