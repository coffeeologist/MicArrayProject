import os
import subprocess
import sys
import pandas as pd

def calcMaxPeakValues(path, windowSize):
    windowFrameSize = (float(windowSize) * 48) #convert from seconds to frames, dependent on audio file sampling rate
    if (os.path.isdir(path) == False):
        if path.endswith(".wav"):
            # Generate the csv with the data
            stringCommand="ffprobe -f lavfi -i amovie="+path+",astats=metadata=1:reset=" + str(windowFrameSize) + " -show_entries frame=pkt_pts_time:frame_tags=lavfi.astats.Overall.Peak_level, -of csv=p=0 -print_format csv>"+path[:-4]+".csv"
            subprocess.call(stringCommand, shell=True)

            df = pd.read_csv(path[:-4]+".csv", header=None)
            maxPeakLevels = df[2].values.tolist()

            result = []
            for i in range (len(maxPeakLevels)):
                if (i % windowFrameSize == windowFrameSize-2 or i == len(maxPeakLevels)-1):
                    result.append(maxPeakLevels[i])

            print(result)
            return result
    return []

calcMaxPeakValues(sys.argv[1], sys.argv[2])

# def amplifyAudio(filePath, windowSize):
#     originalMaxLevels = calcPeakValues(filePath, windowSize)
#     if len(originalMaxLevels) > 0:
#         newPath = filePath[:-4]+"_treated.wav"
#         stringCommand="ffmpeg -i "+filePath+" -filter:a dynaudnorm=f=" +windowSize+ ":m=100:g=3 " + newPath
#         subprocess.call(stringCommand, shell=True)
#         treatedMaxLevels = calcPeakValues(newPath, windowSize)

#         #length of both arrays should be the same since window size is the same and audio length is same
#         amp = list(map(lambda a,b: a-b, treatedMaxLevels, originalMaxLevels))
#         print(amp)
#         return amp
#     return []

# amplifyAudio(sys.argv[1], sys.argv[2])
            

        



    