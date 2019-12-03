import sys
import pandas as pd

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import LabelEncoder

import altair as alt

def getData(path):
    df = pd.read_csv(open(path, "r"),
                     sep = ',',
                     names=["Label", "Overall Peak", "Overall RMS Peak", "Overall RMS Level"],
                     skiprows=1,
                     index_col=False)

    return df

def drawPlot(data, labels):
    source = pd.DataFrame({'LDA1': data[:, 0], 'LDA2': data[:, 1], 'Label': labels})
    source['Label'] = source['Label'].map({0: 'A', 1: 'D', 2: 'S'})

    chart = alt.Chart(source).mark_circle(size=60).encode(
    x='LDA1',
    y='LDA2',
    color='Label')
    chart = chart.configure(background = '#FFFFFF')
    
    chart.save('chart.png', scale_factor=2.0)

def classify(df):
    lda = LinearDiscriminantAnalysis()
    
    df = df.query('Label == "S" or Label == "D" or Label == "A"')

    X = df[["Overall Peak", "Overall RMS Peak", "Overall RMS Level"]].values
    y = df["Label"].values

    enc = LabelEncoder()
    label_encoder = enc.fit(y)
    y = label_encoder.transform(y)

    X_lda = lda.fit_transform(X, y)

    drawPlot(X_lda, y)


# sys.argv[1] = .csv file with labels and 3 ffprobe values
df = getData(sys.argv[1])
classify(df)
