import datetime as dt
from os.path import dirname, join

import numpy as np

import pandas as pd

import pyarrow as pa
import pyarrow.parquet as pq

from bokeh.io import curdoc
from bokeh.layouts import column, gridplot, row
from bokeh.models import ColumnDataSource, DataRange1d, Select, HoverTool, Panel, Tabs, LinearColorMapper, Range1d, MultiChoice
from bokeh.models import NumeralTickFormatter, Title, Label, Paragraph, Div, CustomJSHover, BoxAnnotation
from bokeh.models import ColorBar
from bokeh.palettes import brewer, Spectral6
from bokeh.plotting import figure
from bokeh.embed import server_document
from bokeh.transform import factor_cmap

#################################################################################
# This just loads in the data...
# Alot of this was built of this "cross-fire demo"
# https://github.com/bokeh/bokeh/blob/branch-2.3/examples/app/crossfilter/main.py

background = "#ffffff"

file = "./data"+ "/top20-HS2-exports.parquet"

df = pq.read_table(file).to_pandas()

country_options = df.index.unique(0).to_list()
product_options = df.index.unique(1).to_list()

#print(options)

product = 'ALL PRODUCTS'
country = "MEXICO"

level = "US Dollars"

#################################################################################
#These are functions used in the plot...

def growth_trade(foo):
    # what this function does is take a dataframe and create a relative 
        
    return 100*((foo["exports"]/foo["exports"].shift(12)) - 1)

#################################################################################
# Then this makes the simple plots:

def make_plot():
    
    height = int(1.15*533)
    width = int(1.15*750)
    
    print(country_select.value)
    
    foo = df.loc[country_select.value]
    
    foo = foo.loc[product_select.value]
    # below there is an object of selections which will be one of the values in 
    # the list of options. So the .value then grabs that particular option selected.

    x = foo.index
    
    if level_select.value == 'US Dollars':
        y = foo['exports']
        
    if level_select.value == 'Year over Year % Change':
        y = growth_trade(foo)
        
        
    title = "US EXPORTS to " + country_select.value.title().upper() + " of " + product_select.value.title().upper()

    # This is standard bokeh stuff so far
    plot = figure(x_axis_type="datetime", plot_height = height, plot_width=width, toolbar_location = 'below',
           tools = "box_zoom, reset, pan, xwheel_zoom", title = title,
                  x_range = (dt.datetime(2017,7,1),dt.datetime(2021,1,1)) )

    plot.line(x = x,
              y = y, line_width=3.5, line_alpha=0.75, line_color = "slategray")
        
    # fixed attributes
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = ""
    plot.axis.axis_label_text_font_style = "bold"
    plot.grid.grid_line_alpha = 0.3
    
    TIMETOOLTIPS = """
            <div style="background-color:#F5F5F5; opacity: 0.95; border: 15px 15px 15px 15px;">
             <div style = "text-align:left;">"""
    
    if level_select.value == 'Year over Year % Change':
    
        TIMETOOLTIPS = TIMETOOLTIPS + """
            <span style="font-size: 13px; font-weight: bold"> $data_x{%b %Y}:  $data_y{0}%</span>   
            </div>
            </div>
            """
        
        plot.add_tools(HoverTool(tooltips = TIMETOOLTIPS,  line_policy='nearest', formatters={'$data_x': 'datetime'}))
        
    if level_select.value == 'US Dollars':
    
        TIMETOOLTIPS = TIMETOOLTIPS + """
            <span style="font-size: 13px; font-weight: bold"> $data_x{%b %Y}:  $data_y{$0.0a}</span>   
            </div>
            </div>
            """
        plot.add_tools(HoverTool(tooltips = TIMETOOLTIPS,  line_policy='nearest', formatters={'$data_x': 'datetime'}))
                
    if level_select.value == 'Year over Year % Change':
        if y.max() > 1500:
            plot.y_range.end = 1500
    
    
    
    plot.title.text_font_size = '13pt'
    plot.background_fill_color = background 
    plot.background_fill_alpha = 0.75
    plot.border_fill_color = background 
    
    tradewar_box = BoxAnnotation(left=dt.datetime(2020,3,1), right=dt.datetime(2021,10,11), fill_color='red', fill_alpha=0.1)
    plot.add_layout(tradewar_box)
    
    if country_select.value == "CHINA":
    
        tradewar_box = BoxAnnotation(left=dt.datetime(2018,7,1), right=dt.datetime(2019,10,11), fill_color='red', fill_alpha=0.1)
        plot.add_layout(tradewar_box)
        
        tradewar_box = BoxAnnotation(left=dt.datetime(2020,1,1), right=dt.datetime(2021,12,31), fill_color='blue', fill_alpha=0.1)
        plot.add_layout(tradewar_box)
        
    #p.yaxis.axis_label = 
    plot.yaxis.axis_label_text_font_style = 'bold'
    plot.yaxis.axis_label_text_font_size = "13px"
    
    plot.sizing_mode= "scale_both"
    
    
    if level_select.value != 'Year over Year % Change':
        
        plot.yaxis.formatter = NumeralTickFormatter(format="($0. a)")
        
        plot.yaxis.axis_label = "US Dollars"
        
    if level_select.value == 'Year over Year % Change':
        
        plot.yaxis.axis_label = level_select.value
    
    plot.max_height = height
    plot.max_width = width
    
    plot.min_height = int(0.25*height)
    plot.min_width = int(0.25*width)
    
    return plot

#################################################################################

def update_plot(attrname, old, new):
    layout.children[0] = make_plot()
    
# This part is still not clear to me. but it tells it what to update and where to put it
# so it updates the layout and [0] is the first option (see below there is a row with the
# first entry the plot, then the controls)

level_select = Select(value=level, title='Tranformations', options=['US Dollars', 'Year over Year % Change'])
level_select.on_change('value', update_plot)

#print(sorted(options))
#################################################################################

country_select = Select(value=country, title='Country', options=sorted(country_options), width=400)
#country_select = MultiChoice(value=[country], title='Country', options=sorted(country_options), width=400)
# This is the key thing that creates teh selection object

country_select.on_change('value', update_plot)


#################################################################################

product_select = Select(value=product, title='HS2 Product', options=sorted(product_options), width=400)
# This is the key thing that creates teh selection object

product_select.on_change('value', update_plot)
# Change the value upone selection via the update plot 

div0 = Div(text = """Each category is a 2 digit HS Code. ALL PRODUCTS is the sum of exports across all product catagories.\n
    """, width=400, background = background, style={"justify-content": "space-between", "display": "flex"} )

div1 = Div(text = """Top 20 Countries by export volume and TOTAL which aggregates across all countries in the world.\n
    """, width=400, background = background, style={"justify-content": "space-between", "display": "flex"} )

controls = column(country_select,div1, product_select, div0, level_select)

height = int(1.95*533)
width = int(1.95*675)

layout = row(make_plot(), controls, sizing_mode = "scale_height", max_height = height, max_width = width,
              min_height = int(0.25*height), min_width = int(0.25*width))

curdoc().add_root(layout)
curdoc().title = "us-exports-hs2-products"
