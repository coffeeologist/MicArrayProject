import altair as alt
import pandas as pd
import numpy as np
import sys
import csv
import copy

SCHEME = 'spectral'
WITH_TEXTURE = True

def heatMap(intensity_path, conf_path):
    conf_csv = pd.read_csv(conf_path)
    intensity_csv = pd.read_csv(intensity_path)
    
    for n in range (0, intensity_csv.shape[0]):
        # Currently assumed format of the charts:
        #  12 11 10
        #   9  8  7
        #   6  5  4
        #   3  2  1
        
        intensity_snapshot = intensity_csv.iloc[n, 1:]
        conf_snapshot = conf_csv.iloc[n, 1:] 
        x, y = np.meshgrid(range(1, 4), range(1, 5))
        intensity = x*0 + intensity_snapshot[11-(3*(y-1)+(x-1))]

        confidence = x*0 + conf_snapshot[11-(3*(y-1)+(x-1))]
        # confidence = x*0 + 1

        # Convert this grid to columnar data expected by Altair
        source = pd.DataFrame({'x': x.ravel(),
                            'y': y.ravel(),
                            'intensity': intensity.ravel(),
                            'conf': confidence.ravel()})

        # TODO: possibly make the size arguments an optional commandline argument? 
        resChart = alt.Chart(data=source, height=400, width=600).mark_rect(strokeWidth=100).encode(
            x='x:O',
            y='y:O',
            color=alt.Color('intensity:Q', scale = alt.Scale(scheme=SCHEME, domain=[0.038, 0.000])),
            opacity=alt.Opacity('conf:Q', scale = alt.Scale(domain=[0, 1], range=[0, 1]))
        )

        if(WITH_TEXTURE):
        
            data = pd.DataFrame([dict(id=i) for i in range(0, 144)])
                    
            backgroundGridChart1 = alt.Chart(data, height=400, width=600).transform_calculate(
                row="floor(datum.id/12)"
            ).transform_calculate(
                col="datum.id - datum.row*12"
            ).mark_point(
                filled=True,
                size=100
            ).encode(
                x=alt.X("col:O", axis=None),
                y=alt.Y("row:O", axis=None),
                shape=alt.ShapeValue('circle'),
                color=alt.value('gray')
            )
            alt.layer(backgroundGridChart1, resChart).resolve_scale(y='independent', x='independent').save('chart' + str(n) + '.png')


heatMap(sys.argv[1], sys.argv[2])