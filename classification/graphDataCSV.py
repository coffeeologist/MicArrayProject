import altair as alt
import pandas as pd
import sys

def graph(data):

    source = pd.read_csv(data)

    alt.Chart(source).mark_circle(size=5).encode(
        x='Start',
        y=alt.Y('RMS Variance', scale=alt.Scale(domain=[0.000, 0.000020])),
        color='Label:N'
    ).save('data_csv_graphed.png', scale_factor=2.0)

graph(sys.argv[1])