#!/usr/bin/env python
# coding: utf-8

# In[28]:


import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, CategoricalColorMapper, HoverTool
from bokeh.plotting import figure, curdoc
from bokeh.palettes import viridis
from bokeh.layouts import row, widgetbox
from bokeh.models.widgets import Select, Slider

#Importing and processing data file 
crop = pd.read_csv('crop_production.csv') 

#Cleaning Data 
crop.fillna(np.NaN) 
crop['Season'] = crop.Season.str.strip() 

#Removing Whitespace #Filtering the dataset by Season 
crop_season = crop[crop.Season == 'Whole Year'] 
crop_dt = crop_season.groupby(['State_Name', 'District_Name', 'Crop_Year']).mean().round(1)

crop_dt_year = crop_dt[crop_dt.index.get_level_values('Crop_Year')==2001]
crop_dt_year_state = crop_dt_year[crop_dt_year.index.get_level_values('State_Name')=='Tamil Nadu']

#Creating Column Data Source
source = ColumnDataSource({
    'x': crop_dt_year_state.Area.tolist(), 
    'y': crop_dt_year_state.Production.tolist(), 
    'state': crop_dt_year_state.index.get_level_values('State_Name').tolist(), 
    'district': crop_dt_year_state.index.get_level_values('District_Name').tolist()
})

#Creating color palette for plot
district_list = crop_dt.loc[(['Tamil Nadu']), :].index.get_level_values('District_Name').unique().tolist()
call_colors = viridis(len(district_list))
color_mapper = CategoricalColorMapper(factors=district_list, palette=call_colors)

# Creating the figure
p = figure(
    title = 'Crop Area vs Production',
    x_axis_label = 'Area',
    y_axis_label = 'Production',
    plot_height=900, 
    plot_width=1200,
    tools = [HoverTool(tooltips='@district')]
          )
glyphs = p.circle(x='x', y='y', source=source, size=12, alpha=0.7, 
         color=dict(field='district', transform=color_mapper),
         legend='district')
p.legend.location = 'top_right'

def update_plot(attr, old, new):
    #Update glyph locations
    yr = slider.value
    state  = select.value
    crop_dt_year = crop_dt[crop_dt.index.get_level_values('Crop_Year')==yr]
    crop_dt_year_state = crop_dt_year[crop_dt_year.index.get_level_values('State_Name')==state]
    new_data = {
        'x': crop_dt_year_state.Area.tolist(), 
        'y': crop_dt_year_state.Production.tolist(), 
        'state': crop_dt_year_state.index.get_level_values('State_Name').tolist(), 
        'district': crop_dt_year_state.index.get_level_values('District_Name').tolist()
    }
    source.data = new_data
    #Update colors
    district_list = crop_dt.loc[([state]), :].index.get_level_values('District_Name').unique().tolist()
    call_colors = viridis(len(district_list))
    color_mapper = CategoricalColorMapper(factors=district_list, palette=call_colors)
    glyphs.glyph.fill_color = dict(field='district', transform=color_mapper)
    glyphs.glyph.line_color = dict(field='district', transform=color_mapper)

#Creating Slider for Year
start_yr = min(crop_dt.index.get_level_values('Crop_Year'))
end_yr = max(crop_dt.index.get_level_values('Crop_Year'))
slider = Slider(start=start_yr, end=end_yr, step=1, value=start_yr, title='Year')
slider.on_change('value',update_plot)

#Creating drop down for state
options = list(set(crop_dt.index.get_level_values('State_Name').tolist()))
options.sort()
select = Select(title="State:", value="Tamil Nadu", options=options)
select.on_change('value', update_plot)

layout = row(widgetbox(slider, select), p)
curdoc().add_root(layout)


# In[ ]:




