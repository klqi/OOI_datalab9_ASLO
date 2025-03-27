# create interactive plot with ipywidgets 
from ipywidgets import widgets
import altair as alt
import datetime as dt

# helper function to plot LO1
def plot_stations(all_chl):
    # Determine global axis limits
    time_domain = [all_chl['time'].min(), all_chl['time'].max()]
    chl_domain = [all_chl['chl'].min(), all_chl['chl'].max()+1]
    # Create selection interval
    date_range = (dt.date(2021, 1, 1), dt.date(2022, 1, 1))
    brush = alt.selection_interval(encodings=['x'], value={'x': date_range})
    # keep colors consistent per station
    color_scale = alt.Scale(domain=['Pioneer', 'Irminger'], range=['#1f77b4', '#ff7f0e'])
    # nested helper function to define interactive function
    def plot_time_series(station='All'):
        # set font sizes
        base = alt.Chart(all_chl).mark_point().encode(
            x=alt.X('time:T', scale=alt.Scale(domain=time_domain), title='Time'),
            y=alt.Y('chl:Q', scale=alt.Scale(domain=chl_domain), title='Chlorophyll-a Concentration (µg/L)'),
            color=alt.Color('station:N', scale=color_scale),
            tooltip=['time:T', 'chl:Q', 'station:N']
        ).properties(
            width=700,
            height=400
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
        options=list(all_chl['station'].unique()) + ['All'],
        description='Station:',
        continuous_update=False
    )
    # Display interactive widget
    display(widgets.interactive(plot_time_series, station=station_selector))

import pandas as pd
# helper function to merge all datasets
def combine_datasets(all_chl, all_light, all_no3):
    # merge datasets together
    chl_light_df = pd.merge(all_chl, all_light, how='outer')
    all_df = pd.merge(chl_light_df, all_no3, how='outer')
    # melt wide to long
    all_df_long = pd.melt(all_df, id_vars=['time', 'station', 'chl'], value_vars=['sst', 'light', 'no3'], var_name = 'measurement', value_name  = 'value')
    return all_df_long

# helper function to plot environmental data from each station
def plot_environmental(all_df_long):
    # disable max rows error
    alt.data_transformers.disable_max_rows()
    # Ensure measurement order and assign colors
    measurement_order = ['sst', 'light', 'no3']
    measurement_colors = {'sst': 'blue', 'light': 'orange', 'no3': 'red'}
    all_df_long['measurement'] = pd.Categorical(all_df_long['measurement'], categories=measurement_order, ordered=True)

    # Create a mapping for custom y-axis labels per measurement
    measurement_labels = {
        'sst': 'ºC',
        'light': 'Light (µmol m⁻² s⁻¹)',
        'no3': 'Nitrate (µM)'  
    }

    # Create the base chart for 'chl'
    chl_chart = alt.Chart(all_df_long).mark_line(color='#57A44C', opacity = 0.75).encode(
        x='time:T',
        y=alt.Y('chl:Q', axis=alt.Axis(title='Chlorophyll (µg / L)', titleColor='#57A44C', orient = 'right')),
        tooltip=['time', 'station', 'measurement', 'chl']
    ).properties(width=200, height=150)

    # Create the base chart for 'value'
    value_chart = alt.Chart(all_df_long).mark_line(opacity = 0.75).encode(
        x='time:T',
        y=alt.Y('value:Q', axis=alt.Axis(orient='left'), title = None),
        color=alt.Color('measurement:N', scale=alt.Scale(domain=measurement_order, range=['blue', 'orange', 'red'])),
        tooltip=['time', 'station', 'measurement', 'value']
    ).properties(width=200, height=150)

    # Combine both charts using layer and resolve axes
    combined_chart = alt.layer(chl_chart, value_chart)

    # Facet by station and measurements
    faceted_chart = combined_chart.facet(
        row='measurement:N',
        column='station:N'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_facet(
        spacing=10
    ).configure_view(
        stroke=None
    ).interactive()

    # Add customized row labels
    faceted_chart = faceted_chart.configure_header(
        titleFontSize=12,
        labelFontSize=14,
        # labelExpr=f"datum.value === 'sst' ? '{measurement_labels['sst']}' : datum.value === 'light' ? '{measurement_labels['light']}' : '{measurement_labels['no3']}'"
    )

    faceted_chart.show()