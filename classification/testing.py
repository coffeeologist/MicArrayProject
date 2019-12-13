import os
import subprocess
import sys
import csv
import pandas as pd
import altair as alt
from vega_datasets import data

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

def findValForEachSeg(labels, path, intervalLen, destCSV):
    # stringCommand="ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=1 -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.Flat_factor,lavfi.astats.Overall.Peak_count,lavfi.astats.Overall.Dynamic_range, -of csv=p=0 -print_format csv>"+path[:-4]+".csv"
    stringCommand="ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=1 -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.RMS_difference, -of csv=p=0 -print_format csv>"+path[:-4]+".csv"
    subprocess.call(stringCommand, shell=True)
    # subprocess.call(stringCommand, shell=True)

    # Label the csv (from csvLabeller.py)
    # df = pd.read_csv(path[:-4]+".csv", header=None)
    # df.rename(columns={0: 'frame', 1: 'time', 2: 'Flat factor', 3: 'Peak count', 4: 'Dynamic range'}, inplace=True)
    df = pd.read_csv(path[:-4]+".csv", header=None)
    df.rename(columns={0: 'frame', 1: 'time', 2: 'md'}, inplace=True)
    # stringCommand="ffprobe -f lavfi -i amovie=\""+path+"\",astats=metadata=1:reset=" + str(intervalLen) + " -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.Crest_factor,lavfi.astats.Overall.RMS_trough, -of csv=p=0 -print_format csv>"+path[:-4]+".csv"
    # subprocess.call(stringCommand, shell=True)

    # df = pd.read_csv(path[:-4]+".csv", header=None)
    # print(len(df.column))
    # df.rename(columns={0: 'frame', 1: 'time', 2: 'Crest factor', 3: 'RMS trough'}, inplace=True)
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

        labelClassification.append(classify_dump_crossovers(labels, winStart, winEnd))
                
        winStart = winEnd

    df.insert(1, "Label", labelClassification, True)

    # Save as csv	
    df.to_csv(destCSV, index=False)
    drawBoxPlot(df)

def drawBoxPlot(df):
    # totalEntries = len(df.index)
    # dumpedAmount = len(df[df['Label'] == "DUMPED"].index)

    source = splitByLabel(df)
    boxplots = getBoxPlot(source)
    
    # dumped_table = getSingleValueTextTables('dumped', dumpedAmount, 'Number OfVerallDumped Intervals')
    # total_table = getSingleValueTextTables('total', totalEntries, 'Number of Intervals')
    # numEntries_table = getNumEntries(df, "misc") 
    
    alt.Chart(data=source, height=400, width=200).mark_boxplot(size=40).encode(
        x='Label',
        y=alt.Y('md',
            axis=alt.Axis(title="bleh")
        )
    ).save("chart_rmsDiff.png", scale_factor=2.0)
    
    # statistics = alt.vconcat(numEntries_table, alt.hconcat(dumped_table, total_table, center=True), center=True)
    
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

def splitByLabel(df):
    toDrop = df[ (df['Label'] != "A") & (df['Label'] != "D") & (df['Label'] != "S")].index
    df.drop(toDrop , inplace=True)
    return df

def splitByHumanVsNonHuman(df):
    toDrop = df[ (df['Label'] != "A") & (df['Label'] != "D") & (df['Label'] != "S")].index
    df.drop(toDrop , inplace=True)
    for indexSol, rowSol in df.iterrows():
        if(rowSol['Label'] == "A" or rowSol['Label'] == "D"):
            df.at[indexSol, 'Label'] = "H"

    return df

def splitByHumanVsNonHumanMisc(df):
    for indexSol, rowSol in df.iterrows():
        if(rowSol['Label'] == "A" or rowSol['Label'] == "D"):
            df.at[indexSol, 'Label'] = "H"
        elif(rowSol['Label'] == "S"):
            pass
        elif(rowSol['Label'] == "M" or rowSol['Label'] == "C"):
            df.at[indexSol, 'Label'] = "M"
    toDrop = df[ (df['Label'] != "H") & (df['Label'] != "S") & (df['Label'] != "M")].index
    df.drop(toDrop , inplace=True)
    
    return df

def getNumEntries(df, splitStyle):
    if (splitStyle == 'ads'):
        numEntries_A = getSingleValueTextTables('number', len(df[df['Label'] == 'A'].index), 'Number of A samples')
        numEntries_D = getSingleValueTextTables('number', len(df[df['Label'] == 'D'].index), 'Number of D samples')
        numEntries_S = getSingleValueTextTables('number', len(df[df['Label'] == 'S'].index), 'Number of S samples')
        return alt.hconcat(numEntries_A, numEntries_D, numEntries_S, center=True)
    elif (splitStyle == 'humanNothuman'):
        numEntries_H = getSingleValueTextTables('number', len(df[df['Label'] == 'H'].index), 'Number of H samples')
        numEntries_S = getSingleValueTextTables('number', len(df[df['Label'] == 'S'].index), 'Number of S samples')
        return alt.hconcat(numEntries_H, numEntries_S, center=True)
    else:
        numEntries_H = getSingleValueTextTables('number', len(df[df['Label'] == 'H'].index), 'Number of H samples')
        numEntries_S = getSingleValueTextTables('number', len(df[df['Label'] == 'S'].index), 'Number of S samples')
        numEntries_M = getSingleValueTextTables('number', len(df[df['Label'] == 'M'].index), 'Number of M samples')
        return alt.hconcat(numEntries_H, numEntries_S, numEntries_M, center=True)
        
def getQuartiles(df, splitStyle):
    if (splitStyle == "ads"):
        a = getTextTables(df, "A")
        d = getTextTables(df, "D")
        s = getTextTables(df, "S")
        return alt.vconcat(a, d, s, center=True)
    elif (splitStyle == "humanNothuman"):
        h = getTextTables(df, "H")
        s = getTextTables(df, "S")
        return alt.hconcat(h,s, center=True)
    else:
        h = getTextTables(df, "H")
        m = getTextTables(df, "M")
        s = getTextTables(df, "S")
        return alt.vconcat(h, m, s, center=True)
        
def getBoxPlot(source):
    val = alt.Chart(data=source, height=400, width=200).mark_boxplot(size=40).encode(
        x='Label',
        y=alt.Y('Dynamic range',
            scale=alt.Scale(domain=(-80, 0)),
            axis=alt.Axis(title="Dynamic Range")
        )
    )
    return alt.hconcat(val, center=True)

def drawAComprehensiveBoxPlot(pathToCSV):
    df = pd.read_csv(pathToCSV)
    basic_box_plot = drawBoxPlot(df)
    
    source = splitByHumanVsNonHumanMisc(df)
    quartiles_table = getQuartiles(source, "misc")
    graphs = alt.vconcat(basic_box_plot, quartiles_table, center=True, padding=20).save('chart.png', scale_factor=2.0)

    
    
    
    
    
    
    
    
    
    
    
    
    
    # graphs = alt.vconcat(boxplots, statistics, center=True)

    # return graphs

def drawGridBoxPlotFromCSV(listOfCSV):
    # Currently assumed format of the charts:
    #  12 11 10
    #   9  8  7
    #   6  5  4
    #   3  2  1
    graphs = []
    for i in range (12):
        df = pd.read_csv(listOfCSV[i])
        graph = alt.vconcat(drawBoxPlot(df), getSingleValueTextTables("Mic #", i, listOfCSV[i]), center=True)
        graphs.append(graph)

    row1 = alt.hconcat(graphs[11], graphs[10], graphs[9])
    row2 = alt.hconcat(graphs[8], graphs[7], graphs[6])
    row3 = alt.hconcat(graphs[5], graphs[4], graphs[2])
    row4 = alt.hconcat(graphs[2], graphs[1], graphs[0])

    alt.vconcat(row1, row2, row3, row4, center=True).save("chart.png", scale_factor=2.0)

    pass

def drawGridBoxPlot(labels, pathToFolderOfWAV, intervalLen): # assumes that the .wav files are numbered 01~12
    listOfCSVs = []
    for filename in os.listdir(pathToFolderOfWAV):
        findValForEachSeg(labels, pathToFolderOfWAV + "/" + filename, intervalLen, pathToFolderOfWAV + "/" + filename[:-4]+".csv") 
        listOfCSVs.append(pathToFolderOfWAV + "/" + filename[:-4] + ".csv")
    
    listOfCSVs.sort()
    drawGridBoxPlotFromCSV(listOfCSVs)
    

# argv[1] = .wav file
# argv[2] = .txt labels file
# argv[3] = how many frame rate until resize
# argv[4] = .csv file to store all the audio values
# labels = turnLabelsToDataFrame(sys.argv[2]) # this is a dataframe
# findValForEachSeg(labels, sys.argv[1], sys.argv[3], sys.argv[4])
# drawAComprehensiveBoxPlot(sys.argv[4])


labels = turnLabelsToDataFrame(sys.argv[2]) # this is a dataframe
findValForEachSeg(labels, sys.argv[1], sys.argv[3], sys.argv[4])

# drawGridBoxPlot(labels, sys.argv[1], sys.argv[3])
