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
    timeIntervals = []

    for index, timeBlock in enumerate(stream):
        spectrogram = librosa.stft(timeBlock, window=np.ones, center=False)
        spectrogramMagnitude = librosa.magphase(spectrogram)[0]
        rmsValues = librosa.feature.rms(S = spectrogramMagnitude)
        meanRMS.append(np.mean(rmsValues))
        varianceRMS.append(np.var(rmsValues))

        start = librosa.blocks_to_time(index, 
                                      block_length=size,
                                      hop_length=hopLength,
                                      sr=sampleRate) + absStart
        length = librosa.get_duration(S=spectrogram, sr=sampleRate)
        timeIntervals.append((start, start+length))

    return meanRMS, varianceRMS, timeIntervals

# Converts three lists into a single DataFrame, where
# each row is a window and each column is
# Peak Level, Peak RMS (level), and (average) RMS Level
def createDataFrame(meanRMS, varianceRMS, timeIntervals):
    start = [i[0] for i in timeIntervals]
    end = [i[1] for i in timeIntervals]
    
    tmp = np.array([start, end, meanRMS, varianceRMS])
    tmp = np.transpose(tmp)

    return pd.DataFrame(tmp, columns=["Start", "End", "RMS Level", "RMS Variance"])

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

        if((labStart <= winStart) and (winEnd <= labEnd)):
            result.at[i, "Label"] = labels.at[current, "Label"]

        partitions = []
        while(winEnd > labStart):
            if((labStart <= winStart) and (labEnd <= winEnd)):
                leftOverlap = labEnd - winStart

                current += 1
                labStart = labels.at[current, "Start"]
                labEnd = labels.at[current, "End"]
                
            

    return result

# Uncomment if you want cache cleared before EACH call to script
# librosa.cache.clear()

# sys.argv[1] = .wav file
# sys.argv[2] = frames in slice
# sys.argv[3] = labels file
labels, absStart, absEnd = readLabels(sys.argv[3])
audio, sampleRate, hopLength = loadAudio(sys.argv[1], int(sys.argv[2]), absStart, absEnd)
meanRMS, varianceRMS, timeIntervals = calculateValues(audio, int(sys.argv[2]), hopLength, sampleRate, absStart)
values = createDataFrame(meanRMS, varianceRMS, timeIntervals)

labeledValues = assignLabels(values, labels)