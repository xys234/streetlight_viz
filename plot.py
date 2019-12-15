
from math import pi

from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import ColumnDataSource, GeoJSONDataSource, LinearColorMapper, FactorRange, NumeralTickFormatter, HoverTool, ColorBar
from bokeh.palettes import brewer

import numpy as np
import pandas as pd

def plot_trips(cds, attr, color='blue'):

    p = figure(x_range=FactorRange(*cds.data[attr].tolist()), plot_height=300, plot_width=450)

    # use the palette to colormap based on the the x[1:2] values
    p.vbar(x=attr, top='Trips', width=0.9, source=cds, line_color=None, fill_color=color)

    p.xaxis.minor_tick_line_color = None
    p.xaxis.major_tick_line_color = None
    p.yaxis[0].formatter = NumeralTickFormatter(format="0,")

    p.xaxis.major_label_text_font = "arial"
    p.xaxis.major_label_text_font_size = "9pt"
    p.xaxis.major_label_text_color = "black"
    p.xaxis.major_label_orientation = pi/3

    p.yaxis.major_label_text_font = "arial"
    p.yaxis.major_label_text_font_size = "9pt"
    p.yaxis.major_label_text_color = "black"

    p.title.text_font = "arial"

    tool = HoverTool(
        tooltips=[
            ( 'Trips',  '@{Trips}{0,}' ), 
        ],

        formatters={
            'Trips' : 'numeral',
        },

        mode = 'mouse'

    )
    p.add_tools(tool)
    return p


def plot_zones(zone, trips_origin):
    gdf = pd.merge(zone, trips_origin, left_on="id", right_on="Origin Zone ID", how='left').fillna(0)
    x_min, y_min, x_max, y_max =  gdf.total_bounds
    gs = GeoJSONDataSource(geojson=gdf.to_json())

    tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)

    max_trips = trips_origin.Trips.max()
    if np.isnan(max_trips) :
        max_trips = 10

    tick_labels = {v:str(int(v)) for v in np.linspace(0, max_trips+1, 8)}
    tooltips = [('id','@id'),('Trips', '@{Trips}{0,}')]


    # range bounds supplied in web mercator coordinates
    p = figure(x_range=(x_min, x_max), 
            y_range=(y_min, y_max),x_axis_type="mercator", y_axis_type="mercator", 
            x_axis_location=None, y_axis_location=None,
            plot_height=600, plot_width=900)
    p.add_tile(tile_provider)
    #Define a sequential multi-hue color palette.
    palette = brewer['RdBu'][8]

    #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
    color_mapper = LinearColorMapper(palette = palette, low = 0, high = max_trips)
    p.patches('xs','ys', source = gs,fill_color = {'field' :'Trips', 'transform' : color_mapper},
            line_color = 'black', line_width = 0.25, fill_alpha = 0.5)

    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 800, height = 20,
                        border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
    p.add_layout(color_bar, 'below')
    p.add_tools(HoverTool(tooltips=tooltips,mode = 'mouse'))
    return p