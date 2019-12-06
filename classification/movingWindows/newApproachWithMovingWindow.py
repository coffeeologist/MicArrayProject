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

def findValForEachSeg(labels, path, metric, intervalLen, destCSV, step):
    numIters = int(intervalLen) // int((float(step) * 48))
    res = pd.DataFrame()

    for i in range (numIters):
        stringTrim = "ffmpeg -y -i "+path+" -ss " + str(i) + " -acodec copy "+path[:-4]+"_SHIFT.wav"
        subprocess.call(stringTrim, shell=True)

        stringCommand2 ="ffprobe -f lavfi -i amovie="+path[:-4]+"_SHIFT.wav,astats=metadata=1:reset=" + str(intervalLen) + " -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.Peak_level,lavfi.astats.Overall.RMS_peak,lavfi.astats.Overall.RMS_level, -of csv=p=0 -print_format csv>"+path[:-4]+"_SHIFT.csv"
        subprocess.call(stringCommand2, shell=True)

        df2 = pd.read_csv(path[:-4]+"_SHIFT.csv", header=None)
        df2.rename(columns={0: 'frame', 1: 'time', 2: 'Peak Level', 3: 'RMS Peak', 4: 'RMS Level'}, inplace=True)
        for j in range(len(df2)):
            df2.at[j , "frame"]= str(i)

        df2 = df2.iloc[int(intervalLen)::int(intervalLen)] # starting from row 1, takes every other (intervalLen) row
        
        labelClassification2 = []

        df2.to_csv(path[:-4]+"_SHIFT.csv", index=False)
        # classify each of the window to a label? 
        winStart = i
        for index, row in df2.iterrows():
            row['time'] = i+row['time']
            winEnd = float(row['time'])
            totalTime = float(winEnd - winStart)

            labelClassification2.append(classify_dump_crossovers(labels, winStart, winEnd))
                    
            winStart = winEnd

        df2.insert(1, "Label", labelClassification2, True)
        res = res.append(df2, ignore_index=True)

    res.to_csv(destCSV,index=False)

        
    
    # stringCommand="ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=" + str(intervalLen) + " -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.Peak_level,lavfi.astats.Overall.RMS_peak,lavfi.astats.Overall.RMS_level, -of csv=p=0 -print_format csv>"+path[:-4]+".csv"
    # subprocess.call(stringCommand, shell=True)

    # df = pd.read_csv(path[:-4]+".csv", header=None)
    # df.rename(columns={0: 'frame', 1: 'time', 2: 'Peak Level', 3: 'RMS Peak', 4: 'RMS Level'}, inplace=True)
    # for i in range(len(df)):
    #     df.at[i , "frame"]= str(i)

    # df = df.iloc[int(intervalLen)::int(intervalLen)] # starting from row 1, takes every other (intervalLen) row
    
    # labelClassification = []

    # df.to_csv(path[:-4]+".csv", index=False)
    # # classify each of the window to a label? 
    # winStart = 0
    # for index, row in df.iterrows():
    #     winEnd = float(row['time'])
    #     totalTime = float(winEnd - winStart)

    #     labelClassification.append(classify_dump_crossovers(labels, winStart, winEnd))
                
    #     winStart = winEnd

    # df.insert(1, "Label", labelClassification, True)

    # stringCommand1="ffmpeg -i "+path+" -ss 1 -acodec copy "+path[:-4]+"_SHIFT.wav"
    # subprocess.call(stringCommand1, shell=True)
    
    # stringCommand2 ="ffprobe -f lavfi -i amovie="+path[:-4]+"_SHIFT.wav,astats=metadata=1:reset=" + str(intervalLen) + " -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.Peak_level,lavfi.astats.Overall.RMS_peak,lavfi.astats.Overall.RMS_level, -of csv=p=0 -print_format csv>"+path[:-4]+"_SHIFT.csv"
    # subprocess.call(stringCommand2, shell=True)

    # df2 = pd.read_csv(path[:-4]+"_SHIFT.csv", header=None)
    # df2.rename(columns={0: 'frame', 1: 'time', 2: 'Peak Level', 3: 'RMS Peak', 4: 'RMS Level'}, inplace=True)
    # for i in range(len(df2)):
    #     df2.at[i , "frame"]= str(i)

    # df2 = df2.iloc[int(intervalLen)::int(intervalLen)] # starting from row 1, takes every other (intervalLen) row
    
    # labelClassification2 = []

    # df2.to_csv(path[:-4]+"_SHIFT.csv", index=False)
    # # classify each of the window to a label? 
    # winStart2 = 1
    # for index, row in df2.iterrows():
    #     row['time'] = 1+row['time']
    #     winEnd = float(row['time'])
    #     totalTime = float(winEnd - winStart)

    #     labelClassification2.append(classify_dump_crossovers(labels, winStart, winEnd))
                
    #     winStart = winEnd

    # df2.insert(1, "Label", labelClassification2, True)

    # # Save as csv	
    # df.to_csv(destCSV, index=False)
    # df2.to_csv(destCSV[:-4]+"_SHIFT.csv", index=False)

    # df3 = df.append(df2, ignore_index=True)

    # df3.to_csv(destCSV[:-4]+"_OVERALL.csv",index=False)

def getBaseTable(df):
    return alt.Chart(df, width=200).mark_text().encode(
        y=alt.Y('row_number:O',axis=None)
    ).transform_window(
        row_number='row_number()'
    ).transform_window(
        rank='rank(row_number)'
    ).transform_filter(
        alt.datum.rank<20
    )

def getTextTables(givenDF, name):
    df = givenDF.copy(deep=True)
    toDrop = df[ (df['Label'] != name)].index
    df.drop(toDrop , inplace=True)

    source = df

    rms_quantiles = pd.DataFrame(df['RMS Level'].quantile([1, 0.75, 0.5, 0.25, 0]))
    rmsPeak_quantiles = pd.DataFrame(df['RMS Peak'].quantile([1, 0.75, 0.5, 0.25, 0]))
    peak_quantiles = pd.DataFrame(df['Peak Level'].quantile([1, 0.75, 0.5, 0.25, 0]))

    rms_base_table = getBaseTable(rms_quantiles)
    rmsPeak_base_table = getBaseTable(rmsPeak_quantiles)
    peak_base_table = getBaseTable(peak_quantiles)

    rms_quant_table = rms_base_table.encode(text='RMS Level:Q').properties(title= '[' + name+'] - RMS Level Quartiles')
    rmsPeak_quant_table = rmsPeak_base_table.encode(text='RMS Peak:Q').properties(title='[' + name+'] - RMS Peak Level Quartiles')
    peak_quant_table = peak_base_table.encode(text='Peak Level').properties(title='[' + name + '] - Peak Quartiles')
    
    return alt.hconcat(rms_quant_table, rmsPeak_quant_table, peak_quant_table, center=True, spacing=60) # Combine data tables

def getSingleValueTextTables(name, value, title):
    singleText = pd.DataFrame([{name: value}])
    singleText_base_table = getBaseTable(singleText)
    return singleText_base_table.encode(text=name).properties(title=title)

def drawBoxPlot(pathToCSV):
    df = pd.read_csv(pathToCSV)
    # print(df.to_string());  
    # df = df[df.Label != "A"| df.Label != "D"]

    totalEntries = len(df.index)
    dumpedAmount = len(df[df['Label'] == "DUMPED"].index)

    toDrop = df[ (df['Label'] != "A") & (df['Label'] != "D") & (df['Label'] != "S")].index
    df.drop(toDrop , inplace=True)

    source = df

    rms = alt.Chart(data=source, height=400, width=200).mark_boxplot(size=40).encode(
        x='Label',
        y=alt.Y('RMS Level',
            scale=alt.Scale(domain=(-80, 0)),
            axis=alt.Axis(title="RMS Level (dB)")
        )
    )
    rmsPeak = alt.Chart(data=source, height=400, width=200).mark_boxplot(size=40).encode(
        x='Label',
        y=alt.Y('RMS Peak',
            scale=alt.Scale(domain=(-80, 0)),
            axis=alt.Axis(title="RMS Peak Levels (dB)")
        )
    )
    peak = alt.Chart(data=source, height=400, width=200).mark_boxplot(size=40).encode(
        x='Label',
        y=alt.Y('Peak Level',
            scale=alt.Scale(domain=(-80, 0)),
            axis=alt.Axis(title="Peak Level (dB)")
        )
    )

    a = getTextTables(df, "A")
    d = getTextTables(df, "D")
    s = getTextTables(df, "S")

    numEntries_A = getSingleValueTextTables('number', len(df[df['Label'] == 'A'].index), 'Number of A samples')
    numEntries_D = getSingleValueTextTables('number', len(df[df['Label'] == 'D'].index), 'Number of D samples')
    numEntries_S = getSingleValueTextTables('number', len(df[df['Label'] == 'S'].index), 'Number of S samples')
   
    dumped_table = getSingleValueTextTables('dumped', dumpedAmount, 'Number Of Overall Dumped Intervals')
    total_table = getSingleValueTextTables('total', totalEntries, 'Number of Intervals')
    
    
    statistics = alt.vconcat(alt.hconcat(numEntries_A, numEntries_D, numEntries_S, center = True), alt.hconcat(dumped_table, total_table, center=True), center=True)
    
    graphs = alt.vconcat(alt.hconcat(rms, rmsPeak, peak, center=True), statistics, alt.vconcat(a, d, s, center=True), center=True, padding=20).properties(background='white').save('chart.png', scale_factor=2.0)

# argv[1] = .wav file
# argv[2] = .csv labels file
# argv[3] = how many frame rate until resize
# argv[4] = .csv file to store all the audio values
# argv[5] = number of seconds to step
labels = turnLabelsToDataFrame(sys.argv[2]) # this is a dataframe
findValForEachSeg(labels, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
drawBoxPlot(sys.argv[4])
