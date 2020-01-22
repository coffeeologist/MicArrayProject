import sys
import os
# Set cache for librosa before importing
os.environ['LIBROSA_CACHE_DIR'] = '/tmp/librosa_cache'
import librosa
import numpy as np

import pandas as pd
import altair as alt

# Get ground truths, 
# return DataFrame and overall start/end times of labeled regions
def readLabels(path):
    df = pd.read_csv(open(path, "r"), sep = '\t', names=["Start", "End", "Label"], index_col=False)
    return df, df.at[0, "Start"], df.at[df.size//3 - 1, "End"]

# Create generator for slices of frames of the specified size,
# returns generator
# and parameters for calculating block time indices
def loadAudio(audioPath, size, absStart, absEnd):
    sampleRate = librosa.get_samplerate(audioPath)
    # Assume 48 frames per second (based on ffmpeg), 
    # and that frames contain uniform amount of samples
    # Currently uses disjoint windows
    frameLength = sampleRate // 48
    hopLength = frameLength

    result = librosa.stream(audioPath,
                            offset=absStart,
                            duration=absEnd-absStart,
                            block_length=size,
                            frame_length=frameLength,
                            hop_length=hopLength)

    return result, sampleRate, hopLength

# Returns two lists that contain mean RMS and variance of RMS, 
# along with list of window times
def calculateValues(stream, size, hopLength, sampleRate, absStart):
    meanRMS = []
    varianceRMS = []
    peak = []
    dynamic = []
    timeIntervals = []

    for index, timeBlock in enumerate(stream):
        spectrogram = librosa.stft(timeBlock, window=np.ones, center=False)
        spectrogramMagnitude = librosa.magphase(spectrogram)[0]
        
        peakValue = np.max(spectrogramMagnitude)
        peak.append(peakValue)
        dynamic.append(abs(peakValue - np.min(spectrogramMagnitude)))

        rmsValues = librosa.feature.rms(S = spectrogramMagnitude)
        meanRMS.append(np.mean(rmsValues))
        varianceRMS.append(np.var(rmsValues))

        start = librosa.blocks_to_time(index, 
                                      block_length=size,
                                      hop_length=hopLength,
                                      sr=sampleRate) + absStart
        length = librosa.get_duration(S=spectrogram, sr=sampleRate)
        timeIntervals.append((start, start+length))

    return meanRMS, varianceRMS, peak, dynamic, timeIntervals

# Converts three lists into a single DataFrame, where
# each row is a window and each column is
# Peak Level, Peak RMS (level), and (average) RMS Level
def createDataFrame(meanRMS, varianceRMS, peak, dynamic, timeIntervals):
    start = [i[0] for i in timeIntervals]
    end = [i[1] for i in timeIntervals]
    
    tmp = np.array([start, end, peak, dynamic, meanRMS, varianceRMS])
    tmp = np.transpose(tmp)

    return pd.DataFrame(tmp, columns=["Start", "End", "Peak Level", "Dynamic Range", "RMS Level", "RMS Variance"])

# Assign labels from ground truth to windows
def assignLabels(values, labels):
    result = values
    result["Label"] = ""
    
    current = 0
    for i in range(result.shape[0]):
        winStart = values.at[i, "Start"]
        winEnd = values.at[i, "End"]
        labStart = labels.at[current, "Start"]
        labEnd = labels.at[current, "End"]

        assert(labStart <= winStart)

        # Window completely inside of label
        if(winEnd <= labEnd):
            if((labels.at[current, "Label"][0] == "D") or 
               (labels.at[current, "Label"][0] == "A")):
               result.at[i, "Label"] = "H"
            else:
                result.at[i, "Label"] = labels.at[current, "Label"][0]
        else:
            partitions = []
            while(winEnd > labEnd):
                interval = 0.0
                if(labStart <= winStart):
                    interval = labEnd - winStart
                else:
                    interval = labEnd - labStart
                partitions.append((interval, labels.at[current, "Label"]))
                
                current += 1
                labStart = labels.at[current, "Start"]
                labEnd = labels.at[current, "End"]       
                # Make sure to get final overlap (window hangs into right label)
                if (winEnd > labEnd):
                    partitions.append((winEnd - labStart, labels.at[current, "Label"]))
            
            # Final label assigned is simply largest part of window (no aggregation of same labels occur)
            from operator import itemgetter
            majority = max(partitions, key=itemgetter(0))[1]
            if((majority[0] == "D") or 
               (majority[0] == "A")):
               result.at[i, "Label"] = "H"
            else:
                result.at[i, "Label"] = majority[0]

    return result

# Uncomment if you want cache cleared before EACH call to script
# librosa.cache.clear()

# sys.argv[1] = .wav file
# sys.argv[2] = frames in slice
# sys.argv[3] = labels file
labels, absStart, absEnd = readLabels(sys.argv[3])
audio, sampleRate, hopLength = loadAudio(sys.argv[1], int(sys.argv[2]), absStart, absEnd)
meanRMS, varianceRMS, peak, timeIntervals = calculateValues(audio, int(sys.argv[2]), hopLength, sampleRate, absStart)
values = createDataFrame(meanRMS, varianceRMS, peak, timeIntervals)

labeledValues = assignLabels(values, labels)
