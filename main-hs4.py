import datetime as dt
from os.path import dirname, join

import numpy as np

import pandas as pd

import pyarrow as pa
import pyarrow.parquet as pq

from bokeh.io import curdoc
from bokeh.layouts import column, gridplot, row
from bokeh.models import ColumnDataSource, DataRange1d, Select, HoverTool, Panel, Tabs, LinearColorMapper, Range1d
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

file = "./data"+ "/data-hs4.parquet"

df = pq.read_table(file).to_pandas()

options = df.index.unique(0).to_list()

#print(options)

product = 'HS CODE 1201, Soybeans    , whether or not broken'

level = "US Dollars"

#################################################################################
#These are functions used in the plot...

def growth_trade(foo):
    # what this function does is take a dataframe and create a relative 
        
    return 100*((foo["china_exports"]/foo["china_exports"].shift(12)) - 1)

def cum_trade(foo):
    
    outdf = pd.DataFrame([])
    
    outdf["cuml_trade_2017"] = foo["china_exports"].loc["2017"].cumsum()
        
    outdf.index = pd.date_range(start="2020-01-01", end="2020-12-01", freq = "MS")
    
    outdf["cuml_trade_2020"] = foo["china_exports"].loc["2020"].cumsum()
    
    return outdf

#################################################################################
# Then this makes the simple plots:

def make_plot():
    
    height = int(1.15*533)
    width = int(1.15*750)
    
    foo = df.loc[product_select.value]
    # below there is an object of selections which will be one of the values in 
    # the list of options. So the .value then grabs that particular option selected.

    x = foo.index
    
    if level_select.value == 'US Dollars':
        y = foo['china_exports']
        
    if level_select.value == 'Year over Year % Change':
        y = growth_trade(foo)
        
    if level_select.value == "Cumulative Purchases 2020 vs 2017":
        cuml = cum_trade(foo)
        x = cuml.index
        y2017 = cuml["cuml_trade_2017"]
        y2020 = cuml["cuml_trade_2020"] 

        
    title = "US Exports to China of " + product_select.value.title().upper()
    
    if level_select.value != "Cumulative Purchases 2020 vs 2017":
        
    # This is standard bokeh stuff so far
        plot = figure(x_axis_type="datetime", plot_height = height, plot_width=width, toolbar_location = 'below',
           tools = "box_zoom, reset, pan, xwheel_zoom", title = title,
                  x_range = (dt.datetime(2017,7,1),dt.datetime(2021,1,1)) )

        plot.line(x = x,
              y = y, line_width=3.5, line_alpha=0.75, line_color = "slategray")
    
    if level_select.value == "Cumulative Purchases 2020 vs 2017":
        
        plot = figure(x_axis_type="datetime", plot_height = height, plot_width=width, toolbar_location = 'below',
               tools = "box_zoom, reset, pan", title = title,
                  x_range = (dt.datetime(2020,1,1),dt.datetime(2021,1,1)) )

        plot.line(x = x,
                  y = y2017, line_width=3.5, line_alpha=0.5, line_color = "red", line_dash = "dashed"
                  , legend_label= "2017")
        
        plot.line(x = x,
                  y = y2020, line_width=3.5, line_alpha=0.75, line_color = "darkblue"
                  , legend_label= "2020")
                  
        plot.legend.title = 'Cumulative Purchases'
        plot.legend.location = "top_left"
        plot.legend.title_text_font_style = "bold"
    
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
        
    if level_select.value == "Cumulative Purchases 2020 vs 2017":
        #################################################################################
        singlesource2020 = ColumnDataSource({
                'xs': x.values,
                'ys': y2020.values,
                "dates": np.array(x),
                })

    
        c2020 = plot.circle(x="xs", y="ys", size=35,
                    source = singlesource2020, color = "crimson",alpha=0.0)
    
        singlesource2017 = ColumnDataSource({
                'xs': x.values,
                'ys': y2017.values,
                "dates": np.array(pd.date_range(start="2017-01-01", end="2017-12-01", freq = "MS")),
                })
    
        c2017 = plot.circle(x="xs", y="ys", size=35,
                    source = singlesource2017, color = "darkblue",alpha=0.0)

    
        TIMETOOLTIPS = TIMETOOLTIPS + """
            <span style="font-size: 13px; font-weight: bold"> @dates{%b %Y}:  $data_y{$0.0a}</span>   
            </div>
            </div>
            """
        
        plot.add_tools(HoverTool(tooltips = TIMETOOLTIPS,  line_policy='nearest', formatters={'@dates': 'datetime'}, renderers = [c2017,c2020]))
        
    if level_select.value == 'Year over Year % Change':
        if y.max() > 1500:
            plot.y_range.end = 1500
    
    
    
    plot.title.text_font_size = '13pt'
    plot.background_fill_color = background 
    plot.background_fill_alpha = 0.75
    plot.border_fill_color = background 
    
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

def update_plot(attrname, old, new):
    layout.children[0] = make_plot()
    
# This part is still not clear to me. but it tells it what to update and where to put it
# so it updates the layout and [0] is the first option (see below there is a row with the
# first entry the plot, then the controls)

level_select = Select(value=level, title='Tranformations', options=['US Dollars', 'Year over Year % Change', "Cumulative Purchases 2020 vs 2017"])
level_select.on_change('value', update_plot)

#print(sorted(options))

product_select = Select(value=product, title='Product', options=sorted(options), width=400)
# This is the key thing that creates teh selection object

product_select.on_change('value', update_plot)
# Change the value upone selection via the update plot 

div0 = Div(text = """Each category is a 2 digit HS Code. Only Phase One covered products as defined in Annex 6-1 of The Agreement within that HS Code are shown. Red marks the period of Section 301 tariffs and retaliation. Blue is period of agreement.\n
    \n
    \n
    """, width=400, background = background, style={"justify-content": "space-between", "display": "flex"} )

div1 = Div(text = """Transformations: US Dollars, year over year growth rate and cumulative purchases in 2017 vs 2020.\n The later transformation cumulates Chinese purchases over each month in 2017 and 2020 and compares each. Because 2017 is the benchmark year for The Agreement, this measure provides a sense, for each product category, China's progress towards meeting their purchase commitments.\n
    """, width=400, background = background, style={"justify-content": "space-between", "display": "flex"} )

controls = column(product_select, div0, level_select, div1)

height = int(1.95*533)
width = int(1.95*675)

layout = row(make_plot(), controls, sizing_mode = "scale_height", max_height = height, max_width = width,
              min_height = int(0.25*height), min_width = int(0.25*width))

curdoc().add_root(layout)
curdoc().title = "us-china-products"
