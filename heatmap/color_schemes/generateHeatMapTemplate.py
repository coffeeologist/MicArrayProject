import altair as alt
import numpy as np
import pandas as pd

x, y = np.meshgrid(range(0, 10), range(0, 10))
intensity = x
confidence = y/9

# Convert this grid to columnar data expected by Altair
source = pd.DataFrame({'x': x.ravel(),
                     'y': y.ravel(),
                     'intensity': intensity.ravel(),
                     'confidence': confidence.ravel()})

gradient = alt.Chart(source, height=600, width=600).mark_rect().encode(
    x='x:O',
    y='y:O',
    color=alt.Color('intensity:Q', scale = alt.Scale(scheme='reds')),
    opacity=alt.Opacity('confidence:Q', scale = alt.Scale(domain=[0, 1], range=[0, 1]))
).save('reds_palette.png')
'''
blank1, blank = np.meshgrid(range(0, 10), range(0, 10))
blank2 = blank*0 + 10
backgroundGrid = pd.DataFrame({'x': blank1.ravel(), 'y':blank2.ravel()})
backgroundGrid = pd.DataFrame({
    'a': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    'b': [9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
})
backgroundGridChart1 = alt.Chart(backgroundGrid, height=600, width=600).mark_bar(size=10).encode(x='a', y='b')
alt.layer(backgroundGridChart1, gradient).save('spectral_palette_with_texture.png')
'''
