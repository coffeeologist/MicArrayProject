import os
import subprocess
import sys
import csv
import pandas as pd
import altair as alt
import time

def performanceCheck(truthLabels, classifiedLabels):
    #truthLabels is ground truth text file
    #classifiedLabels is labels generated from classifier (in same format as ground truth)
    truth = turnLabelsToDataFrame(truthLabels)
    classified = turnLabelsToDataFrame(classifiedLabels)

    score = 0.0

    for index, row in classified.iterrows():
        winStart = float(row['from'])
        winEnd = float(row['to'])
        genLab = row['label'][0:1]
        temp = calculateScore(truth, winStart, winEnd, genLab)
        score += temp
    return score / (len(classified.index))

def calculateScore(truth, winStart, winEnd, genLab):
    composition = {}
    for indexSol, rowSol in truth.iterrows():
        labStart = float(rowSol['from'])
        labEnd = float(rowSol['to'])
        lab = rowSol['label']

        if (winStart < labStart and winEnd < labStart):
            break
        if (winStart > labStart and winStart > labEnd):
            continue

        if(labStart <= winStart and winEnd <= labEnd):
            if (lab == genLab):
                return 1.0
            return 0.0
        elif (winStart < labStart and winEnd > labEnd):
            if lab in composition:
                current = composition.get(lab)
                assert((labEnd-labStart)/(winEnd-winStart) >= 0)
                current += (labEnd-labStart)/(winEnd-winStart)
                composition[lab] = current
            else:
                assert((labEnd-labStart)/(winEnd-winStart) >= 0)
                composition[lab] = (labEnd-labStart)/(winEnd-winStart)
        elif (winStart < labStart):
            if lab in composition:
                current = composition.get(lab)
                assert((winEnd-labStart)/(winEnd-winStart) >= 0)
                current += (winEnd-labStart)/(winEnd-winStart)
                composition[lab] = current
            else:
                assert((winEnd-labStart)/(winEnd-winStart) >= 0)
                composition[lab] = (winEnd-labStart)/(winEnd-winStart)
        elif (winEnd > labEnd):
            if lab in composition:
                current = composition.get(lab)
                current += (labEnd-winStart)/(winEnd-winStart)
                assert((labEnd-winStart)/(winEnd-winStart) >= 0)
                composition[lab] = current
            else:
                assert((labEnd-winStart)/(winEnd-winStart) >= 0)
                composition[lab] = (labEnd-winStart)/(winEnd-winStart)
    if (genLab in composition):
        return composition[genLab]
    return 0.0

# takes a .txt label file (generated from audacity) and turns into a csv for processing
def turnLabelsToDataFrame(path):
    txt_file = path
    #csv_file = path[:-4]+".csv"

    df = pd.read_csv(open(txt_file, "r"), sep = '\t', names=["from", "to", "label"], index_col=False)
    # df.to_csv(csv_file)

    return df

print(performanceCheck(sys.argv[1], sys.argv[2]))