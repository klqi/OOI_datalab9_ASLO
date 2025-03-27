# create interactive plot with ipywidgets 
from ipywidgets import widgets
import altair as alt
import datetime as dt

# Determine global axis limits
time_domain = [all_chl['time'].min(), all_chl['time'].max()]
chl_domain = [all_chl['chl'].min(), all_chl['chl'].max()+1]

# Create selection interval
date_range = (dt.date(2021, 1, 1), dt.date(2022, 1, 1))
brush = alt.selection_interval(encodings=['x'], value={'x': date_range})

# keep colors consistent per station
color_scale = alt.Scale(domain=['Pioneer', 'Irminger'], range=['#1f77b4', '#ff7f0e'])

# Define interactive function
def plot_time_series(station='All'):
    # set font sizes
    base = alt.Chart(all_chl).mark_point().encode(
        x=alt.X('time:T', scale=alt.Scale(domain=time_domain), title='Time'),
        y=alt.Y('chl:Q', scale=alt.Scale(domain=chl_domain), title='Chlorophyll-a Concentration (µg/L)'),
        color=alt.Color('station:N', scale=color_scale),
        tooltip=['time:T', 'chl:Q', 'station:N']
    ).properties(
        width=800,
        height=500
    )

    if station != 'All':
        base = base.transform_filter(alt.datum.station == station)

    upper = base.encode(alt.X('time:T').scale(domain=brush))

    lower = base.properties(
        height=60
    ).add_params(brush)
    
    display(upper & lower)

# Create dropdown widget
station_selector = widgets.Dropdown(
    options=['All'] + list(all_chl['station'].unique()),
    description='Station:',
    continuous_update=False
)
# Display interactive widget
display(widgets.interactive(plot_time_series, station=station_selector))