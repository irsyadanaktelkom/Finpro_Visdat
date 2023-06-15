import streamlit as st
import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, CategoricalColorMapper, HoverTool
from bokeh.plotting import figure
from bokeh.palettes import viridis

# Importing and processing data file
crop = pd.read_csv('crop_production.csv')

# Cleaning Data
crop.fillna(np.NaN)
crop['Season'] = crop.Season.str.strip()

# Removing Whitespace
# Filtering the dataset by Season
crop_season = crop[crop.Season == 'Whole Year']
crop_season['Area'] = pd.to_numeric(crop_season['Area'], errors='coerce')
crop_season['Production'] = pd.to_numeric(crop_season['Production'], errors='coerce')
crop_dt = crop_season.groupby(['State_Name', 'District_Name', 'Crop_Year']).mean().round(1)

crop_dt_year = crop_dt[crop_dt.index.get_level_values('Crop_Year') == 2001]
crop_dt_year_state = crop_dt_year[crop_dt_year.index.get_level_values('State_Name') == 'Tamil Nadu']

# Creating Column Data Source
source = ColumnDataSource({
    'x': crop_dt_year_state.Area.tolist(),
    'y': crop_dt_year_state.Production.tolist(),
    'state': crop_dt_year_state.index.get_level_values('State_Name').tolist(),
    'district': crop_dt_year_state.index.get_level_values('District_Name').tolist()
})

# Creating color palette for plot
district_list = crop_dt.loc[(['Tamil Nadu']), :].index.get_level_values('District_Name').unique().tolist()
call_colors = viridis(len(district_list))
color_mapper = CategoricalColorMapper(factors=district_list, palette=call_colors)

# Creating the figure
p = figure(
    title='Crop Area vs Production',
    x_axis_label='Area',
    y_axis_label='Production',
    plot_height=900,
    plot_width=1200,
    tools=[HoverTool(tooltips='@district')]
)
glyphs = p.circle(x='x', y='y', source=source, size=12, alpha=0.7,
                  color=dict(field='district', transform=color_mapper),
                  legend='district')
p.legend.location = 'top_right'


@st.cache
def get_filtered_data(year, state):
    crop_dt_year = crop_dt[crop_dt.index.get_level_values('Crop_Year') == year]
    crop_dt_year_state = crop_dt_year[crop_dt_year.index.get_level_values('State_Name') == state]
    new_data = {
        'x': crop_dt_year_state.Area.tolist(),
        'y': crop_dt_year_state.Production.tolist(),
        'state': crop_dt_year_state.index.get_level_values('State_Name').tolist(),
        'district': crop_dt_year_state.index.get_level_values('District_Name').tolist()
    }
    return new_data


@st.cache
def get_district_list(state):
    district_list = crop_dt.loc[([state]), :].index.get_level_values('District_Name').unique().tolist()
    return district_list


def update_plot(attr, old, new):
    # Update glyph locations
    yr = slider.value
    state = select.value
    new_data = get_filtered_data(yr, state)
    source.data = new_data
    # Update colors
    district_list = get_district_list(state)
    call_colors = viridis(len(district_list))
    color_mapper = CategoricalColorMapper(factors=district_list, palette=call_colors)
    glyphs.glyph.fill_color = dict(field='district', transform=color_mapper)
    glyphs.glyph.line_color = dict(field='district', transform=color_mapper)


# Creating Slider for Year
start_yr = int(min(crop_dt.index.get_level_values('Crop_Year')))
end_yr = int(max(crop_dt.index.get_level_values('Crop_Year')))
default_yr = start_yr
slider = st.slider('Year', start=start_yr, end=end_yr, value=default_yr, step=1)
slider.on_change('value', update_plot)

# Creating drop down for state
options = list(set(crop_dt.index.get_level_values('State_Name').tolist()))
options.sort()
default_state = "Tamil Nadu"
select = st.selectbox("State:", options, index=options.index(default_state))
select.on_change('value', update_plot)

st.bokeh_chart(p)
