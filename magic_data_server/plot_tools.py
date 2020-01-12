
from __future__ import absolute_import, division, print_function

from builtins import (open, str, range,
                      object)


from bokeh.layouts import row, widgetbox, gridplot
from bokeh.models import CustomJS, Slider, HoverTool, ColorBar, LinearColorMapper, LabelSet, ColumnDataSource

from bokeh.embed import components
from bokeh.plotting import figure
from matplotlib import  pylab as plt
import  numpy as np



class DataPlot(object):
    def __init__(self):

        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.subplots(1, 1)

    def add_data_plot(self,
                      x,
                      y,
                      dx=None,
                      dy=None,
                      label=None,
                      color=None,
                      fmt='o',
                      ms=None,
                      mew=None,
                      loglog=True,
                      grid=False):



        # get x,y,dx,dy from SEDdata
        if dx is None:
            dx = np.zeros(len(x))

        if dy is None:
            dy = np.zeros(len(y))

        # set color
        #if color is None:
        #    color = self.counter



        line = self.ax.errorbar(x, y, xerr=dx, yerr=dy, fmt=fmt, label=label, ms=ms, mew=mew)
        if loglog is True:
            self.ax.set_xscale("log", nonposx='clip')
            self.ax.set_yscale("log", nonposy='clip')


        if grid is True:
            self.ax.grid()

        self.ax.legend()

    def add_sed(self,sed_table,label=None,color=None):
        if label is None:
            label=sed_table.meta['Source']
        self.add_data_plot(x=sed_table['freq'],
                           y=sed_table['nufnu'],
                           dx=[sed_table['freq_elo'], sed_table['freq_eup']],
                           dy=[sed_table['nufnu_elo'], sed_table['nufnu_eup']],
                           label=label,
                           color=color)

        self.ax.set_ylabel(sed_table['nufnu'].unit)
        self.ax.set_xlabel(sed_table['freq'].unit)
        #self.ax.set_ylim(5E-14, 1E-9)
        #self.ax.grid()

    def add_lc(self,lc_table):
        self.add_data_plot(x=lc_table['tstart'],
                           y=lc_table['nufnu'],
                           dy=[lc_table['nufnu_elo'],lc_table['nufnu_eup']],
                           label=lc_table.meta['Source'],
                           loglog=False)

        self.ax.set_ylabel(lc_table['nufnu'].unit)
        self.ax.set_xlabel(lc_table['tstart'].unit)
        #self.ax.grid()
        #self.ax.legend()

class ScatterPlot(object):

    def __init__(self,w,h,x_label=None,y_label=None,x_range=None,y_range=None,title=None,y_axis_type='linear',x_axis_type='linear'):
        hover = HoverTool(tooltips=[("x", "$x"), ("y", "$y")])

        self.fig = figure(title=title, width=w, height=h,x_range=x_range,y_range=y_range,
                          y_axis_type=y_axis_type,
                          x_axis_type=x_axis_type,
                     tools=[hover, 'pan,box_zoom,box_select,wheel_zoom,reset,save,crosshair'])

        if x_label is not None:
            self.fig.xaxis.axis_label = x_label

        if y_label is not None:
            self.fig.yaxis.axis_label = y_label

        self.fig.add_tools(hover)

    def add_errorbar(self, x, y, xerr=None, yerr=None, color='red',
                 point_kwargs={}, error_kwargs={}):

        self.fig.circle(x, y, color=color, **point_kwargs)

        if xerr is not None:
            x_err_x = []
            x_err_y = []
            for px, py, err in zip(x, y, xerr):
                x_err_x.append((px - err, px + err))
                x_err_y.append((py, py))
            self.fig.multi_line(x_err_x, x_err_y, color=color, **error_kwargs)

        if yerr is not None:
            y_err_x = []
            y_err_y = []
            for px, py, err in zip(x, y, yerr):
                y_err_x.append((px, px))
                y_err_y.append((py - err, py + err))
            self.fig.multi_line(y_err_x, y_err_y, color=color, **error_kwargs)



    def add_step_line(self,x,y,legend=None):
        #print('a')
        self.fig.step(x,y,name=legend, mode="center")
        #print('b')

    def add_line(self,x,y,legend=None,color=None):
        self.fig.line(x,y,legend=legend,line_color=color)

    def get_html_draw(self):
        self.fig.sizing_mode = 'scale_width'
        layout = row(
            self.fig
        )

        layout.sizing_mode = 'scale_width'

        return components(layout)
