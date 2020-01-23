import altair as alt
import numpy as np
import pandas as pd

# Settings
COLOR_SCHEME = 'custom'
WITH_TEXTURE = True

# Code to make the swatches
x, y = np.meshgrid(range(0, 10), range(0, 10))
intensity = x
confidence = (y/9) * 100 + 1

# Convert this grid to columnar data expected by Altair
source = pd.DataFrame({'x': x.ravel(),
                     'y': y.ravel(),
                     'intensity': intensity.ravel(),
                     'confidence': confidence.ravel()})

# original code that makes palettes
# gradient = alt.Chart(source).mark_rect().encode(
#     x='x:O',
#     y='y:O',
#     color=alt.Color('confidence:Q', scale = alt.Scale(scheme=COLOR_SCHEME, domain=[0,1])),
#     opacity=alt.Opacity('intensity:Q', scale = alt.Scale(domain=[0, 9], range=[0.1, 1]))
# )

# after briefing David, he suggested to have silence be white (so a white->red scale)
gradient = alt.Chart(source).mark_rect().encode(
    x='x:O',
    y='y:O',
    color=alt.Color('intensity:Q', legend=alt.Legend(orient='bottom'), scale = alt.Scale(type='linear', domain=[0,9], range=['#ffffff', '#ffe6e6', '#ffcccc', 'ffb3b3', '#ff9999', '#ff8080', '#ff6666', '#ff4d4d', '#ff3333', '#ff1a1a', '#ff0000', '#e60000', '#cc0000'])),
    opacity=alt.Opacity('confidence:Q', scale = alt.Scale(type='log', domain=[1, 100], range=[0.2, 1]))
)
if (WITH_TEXTURE):
    data = pd.DataFrame([dict(id=i) for i in range(0, 99)])

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