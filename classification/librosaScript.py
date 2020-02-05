import sys
import os
# Set cache for librosa before importing
os.environ['LIBROSA_CACHE_DIR'] = '/tmp/librosa_cache'
os.environ['LIBROSA_CACHE_LEVEL'] = '20'
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

#calculates zero crossing rate
#returns np array
def zeroCross(audioPath, absStart, absEnd, hopLength):
    y, sr = librosa.load(audioPath , sr=None, offset=absStart, duration=absEnd-absStart)
    frameLength = sr // 48
    arr = librosa.feature.zero_crossing_rate(y,frame_length=frameLength, hop_length=hopLength)[0]
    arr = np.split(arr,[len(arr) - len(arr) % 12])[0].reshape(-1,12)
    arr = np.mean(arr, axis=1)
    return arr


# Converts three lists into a single DataFrame, where
# each row is a window and each column is
# Peak Level, Peak RMS (level), and (average) RMS Level
def createDataFrame(meanRMS, varianceRMS, peak, dynamic, timeIntervals, zeroCrossings):
    start = [i[0] for i in timeIntervals]
    end = [i[1] for i in timeIntervals]
    pad = lambda a, i: a[0: i] if a.shape[0] > i else np.hstack((a, np.zeros(i - a.shape[0])))
    zeroCrossings = pad(zeroCrossings, len(varianceRMS))
    
    tmp = np.array([start, end, peak, dynamic, meanRMS, varianceRMS, zeroCrossings]) 
    tmp = np.transpose(tmp)

    return pd.DataFrame(tmp, columns=["Start", "End", "Peak Level", "Dynamic Range", "RMS Level", "RMS Variance", "Zero Crossing Rate"])

# Assign labels from ground truth to windows
def assignLabels(values, labels):
    result = values
    result["Label"] = ""
    
    for i in range(result.shape[0]):
        winStart = values.at[i, "Start"]
        winEnd = values.at[i, "End"]

        composition = {}
        for indexSol, rowSol in labels.iterrows():
            labStart = float(rowSol['Start'])
            labEnd = float(rowSol['End'])
            lab = rowSol['Label'][0:1]

            if (winStart < labStart and winEnd < labStart):
                break
            if (winStart > labStart and winStart > labEnd):
                continue

            if(labStart <= winStart and winEnd <= labEnd):
                if((lab == "D") or (lab == "A")):
                    result.at[i, "Label"] = "H"
                else:
                    result.at[i, "Label"] = lab
                break

            elif (winStart < labStart and winEnd > labEnd):
                if lab in composition:
                    currentt = composition.get(lab)
                    assert((labEnd-labStart)/(winEnd-winStart) >= 0)
                    currentt += (labEnd-labStart)/(winEnd-winStart)
                    composition[lab] = currentt
                else:
                    assert((labEnd-labStart)/(winEnd-winStart) >= 0)
                    composition[lab] = (labEnd-labStart)/(winEnd-winStart)
            elif (winStart < labStart):
                if lab in composition:
                    currentt = composition.get(lab)
                    assert((winEnd-labStart)/(winEnd-winStart) >= 0)
                    currentt += (winEnd-labStart)/(winEnd-winStart)
                    composition[lab] = currentt
                else:
                    assert((winEnd-labStart)/(winEnd-winStart) >= 0)
                    composition[lab] = (winEnd-labStart)/(winEnd-winStart)
            elif (winEnd > labEnd):
                if lab in composition:
                    currentt = composition.get(lab)
                    currentt += (labEnd-winStart)/(winEnd-winStart)
                    assert((labEnd-winStart)/(winEnd-winStart) >= 0)
                    composition[lab] = currentt
                else:
                    assert((labEnd-winStart)/(winEnd-winStart) >= 0)
                    composition[lab] = (labEnd-winStart)/(winEnd-winStart)
        
            import operator
            majority = max(composition, key = composition.get)
            if((majority == "D") or (majority == "A")):
                result.at[i, "Label"] = "H"
            else:
                result.at[i, "Label"] = majority

    return result

# Uncomment if you want cache cleared before EACH call to script
#librosa.cache.clear()

# sys.argv[1] = .wav file
# sys.argv[2] = frames in slice
# sys.argv[3] = labels file
labels, absStart, absEnd = readLabels(sys.argv[3])
audio, sampleRate, hopLength = loadAudio(sys.argv[1], int(sys.argv[2]), absStart, absEnd)
meanRMS, varianceRMS, peak, dynamic, timeIntervals = calculateValues(audio, int(sys.argv[2]), hopLength, sampleRate, absStart)
zeroCrossings = zeroCross(sys.argv[1], absStart, absEnd, hopLength)
values = createDataFrame(meanRMS, varianceRMS, peak, dynamic, timeIntervals, zeroCrossings)

labeledValues = assignLabels(values, labels)
labeledValues.to_csv("data-new.csv")
