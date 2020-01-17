import altair as alt
import numpy as np
import pandas as pd

# Settings
COLOR_SCHEME = 'viridis'
WITH_TEXTURE = True

# Code to make the swatches
x, y = np.meshgrid(range(0, 10), range(0, 10))
intensity = x
confidence = y/9

# Convert this grid to columnar data expected by Altair
source = pd.DataFrame({'x': x.ravel(),
                     'y': y.ravel(),
                     'intensity': intensity.ravel(),
                     'confidence': confidence.ravel()})

gradient = alt.Chart(source).mark_rect().encode(
    x='x:O',
    y='y:O',
    color=alt.Color('intensity:Q', scale = alt.Scale(scheme=COLOR_SCHEME)),
    opacity=alt.Opacity('confidence:Q', scale = alt.Scale(domain=[0, 1], range=[0, 1]))
)

if (WITH_TEXTURE):
    '''
    blank1, blank = np.meshgrid(range(0, 10), range(0, 10))
    blank2 = blank*0 + 10
    backgroundGrid = pd.DataFrame({'x': blank1.ravel(), 'y':blank2.ravel()})
    backgroundGrid = pd.DataFrame({
        'a': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        'b': [9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
    })
    backgroundGridChart1 = alt.Chart(backgroundGrid, height=600, width=600).mark_bar(size=10).encode(x='a', y='b')
    '''

        
    data = pd.DataFrame([dict(id=i) for i in range(0, 99)])

    person = (
        "M1.7 -1.7h-0.8c0.3 -0.2 0.6 -0.5 0.6 -0.9c0 -0.6 "
        "-0.4 -1 -1 -1c-0.6 0 -1 0.4 -1 1c0 0.4 0.2 0.7 0.6 "
        "0.9h-0.8c-0.4 0 -0.7 0.3 -0.7 0.6v1.9c0 0.3 0.3 0.6 "
        "0.6 0.6h0.2c0 0 0 0.1 0 0.1v1.9c0 0.3 0.2 0.6 0.3 "
        "0.6h1.3c0.2 0 0.3 -0.3 0.3 -0.6v-1.8c0 0 0 -0.1 0 "
        "-0.1h0.2c0.3 0 0.6 -0.3 0.6 -0.6v-2c0.2 -0.3 -0.1 "
        "-0.6 -0.4 -0.6z"
    )

    backgroundGridChart1 = alt.Chart(data).transform_calculate(
        row="floor(datum.id/10)"
    ).transform_calculate(
        col="datum.id - datum.row*10"
    ).mark_point(
        filled=True,
        size=50
    ).encode(
        x=alt.X("col:O", axis=None),
        y=alt.Y("row:O", axis=None),
        shape=alt.ShapeValue('circle'),
        color=alt.value('gray')
    )
    alt.layer(backgroundGridChart1, gradient).save(COLOR_SCHEME + '_palette_with_texture.png', scale_factor=2.0)

else:
    gradient.save(COLOR_SCHEME+"_palette.png")