import os
import subprocess
import sys
import csv
import pandas as pd
import altair as alt

def generate_data_in_df(path, intervalLen):
    csv_path = path[:-4]+".csv"

    stringCommand="ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=" + str(intervalLen) + " -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.Peak_level,lavfi.astats.Overall.RMS_peak,lavfi.astats.Overall.RMS_level, -of csv=p=0 -print_format csv>"+ csv_path
    subprocess.call(stringCommand, shell=True)

    df = pd.read_csv(path[:-4]+".csv", header=None)
    df.rename(columns={0: 'frame', 1: 'End Time', 2: 'Peak Level', 3: 'RMS Peak', 4: 'RMS Level'}, inplace=True)
    for i in range(len(df)):
        df.at[i , "frame"]= str(i)

    df = df.iloc[int(intervalLen)::int(intervalLen)] # starting from row 1, takes every other (intervalLen) row

    startTime = (df['End Time'].tolist())[:-1]
    startTime.insert(0, 0.0)
    df.insert(1, "Start Time", startTime)

    df.to_csv(csv_path, index=False)

    return df

def classify(path, intervalLen):
    df = generate_data_in_df(path, intervalLen)

    classification_result = []

    for index, row in df.iterrows():
        peak = float(row['Peak Level'])
        if(-100 < peak < -53):
            classification_result.append('S')
        else:
            classification_result.append('D or A')

    df.insert(1, "Label", classification_result)

    post_process(df)

def post_process(df):
    startInterval = 0.0
    endInterval = 0.0
    currentLabel = ''

    res = []
    for index, row in df.iterrows():
        lab = row['Label']
        if(lab != currentLabel):
            res.append({"1-start": startInterval, "2-end": endInterval, "3-label": currentLabel})

            # update to be counting for the new label
            startInterval = endInterval
            endInterval = row['End Time']
            currentLabel = lab
        else:
            endInterval = row['End Time']


    res_df = pd.DataFrame(res)
    res_df.to_csv("machine_generated_labels.txt", sep="\t", quoting=csv.QUOTE_NONE, index=False)


# 1 = path to csv
# 2 = interval length / window size / number to reset
classify(sys.argv[1], sys.argv[2])