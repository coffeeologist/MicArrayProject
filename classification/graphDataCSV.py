import altair as alt
import pandas as pd
import sys

def graph(data):

    source = pd.read_csv(data)

    '''
    toDrop = source[ (source['Label'] != 'S')].index
    source.drop(toDrop , inplace=True)
    
    '''
    alt.Chart(source).mark_bar().encode(
        x=alt.X('Dynamic Range:Q', bin=alt.Bin(extent=[0,5], step=0.05)),
        y='count()',
        color='Label:N'
    ).save('data_csv_graphed.png', scale_factor=2.0)

graph(sys.argv[1])