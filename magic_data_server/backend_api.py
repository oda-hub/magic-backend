
from __future__ import absolute_import, division, print_function

from builtins import (open, str, range,
                      object)

from flask import Flask, jsonify, abort,request,render_template,Response
from flask_restplus import Api, Resource,reqparse
from flask.json import JSONEncoder

from astropy.table import Table
import json
import yaml
import pickle
import os
import  numpy as np

from .client_api import    DataPlot

import base64
from io import BytesIO

from bokeh.layouts import row, widgetbox, gridplot
from bokeh.models import CustomJS, Slider, HoverTool, ColorBar, LinearColorMapper, LabelSet, ColumnDataSource

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.palettes import Plasma256


try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from magic_data_server import  conf_dir


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            print('hi')
            return list(obj)

        return JSONEncoder.default(self, obj)


template_dir =os.path.abspath(os.path.dirname(__file__))+'/templates'
print ('template_dir',template_dir)
micro_service = Flask("micro_service",template_folder=template_dir)

micro_service.json_encoder = CustomJSONEncoder


api= Api(app=micro_service, version='1.0', title='MAGIC back-end API',
    description='API to extract data for MAGIC Telescope\n Author: Andrea Tramacere',)


ns_conf = api.namespace('api/v1.0/magic', description='data access')



def get_path(file_name):
    config = micro_service.config.get('conf')
    file_path = os.path.join(config.data_root_path, file_name)
    return file_path

def output_html(data, code, headers=None):
    resp = Response(data, mimetype='text/html', headers=headers)
    resp.status_code = code
    return resp

class Configurer(object):
    def __init__(self, cfg_dict):
        self._valid=['port','url','data_root_path','catalog_file','source_name_field','MW_file_kw','MAGIC_file_kw']
        self._validate(cfg_dict)

        for k in cfg_dict.keys():
            setattr(self,k,cfg_dict[k])


    def _validate(self,cfg_dict):
        for k in cfg_dict.keys():
            if k not in self._valid:
                raise RuntimeError('conf key',k,'is not valid')


    @classmethod
    def from_conf_file(cls, conf_file):

        def_conf_file=os.path.join(conf_dir,'config.yml')

        with open(def_conf_file, 'r') as ymlfile:
            cfg_dict=yaml.load(ymlfile,Loader=yaml.FullLoader)

        with open(conf_file, 'r') as ymlfile:

            user_cfg_dict = yaml.load(ymlfile,Loader=yaml.FullLoader)

        for k in user_cfg_dict.keys():
            cfg_dict[k]=user_cfg_dict[k]

        return Configurer(cfg_dict)

class APIerror(Exception):

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message

        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        print('API Error Message',message)

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error_message'] = self.message
        return rv


class MAGICTable(object):

    def __init__(self,table_object,name='astropy table', meta_data={}):
        self.name=name
        self.meta_data=meta_data
        self.table=table_object


    @classmethod
    def from_file(cls,file_path,format,name):

        table=Table.read(file_path, format=format)

        meta=None

        if hasattr(table,'meta'):
            meta=table.meta

        return cls(table,name,meta_data=meta)


    def encode(self,use_binary=False,to_json = False):

        _o_dict = {}
        _o_dict['binary']=None
        _o_dict['ascii']=None

        if use_binary is True:
            _binarys = base64.b64encode(pickle.dumps(self.table, protocol=2)).decode('utf-8')
            _o_dict['binary'] = _binarys
        else:
            fh=StringIO()
            self.table.write(fh, format='ascii.ecsv')
            _text = fh.getvalue()
            fh.close()
            _o_dict['ascii'] = _text

        _o_dict['name']=self.name
        _o_dict['meta_data']=json.dumps(self.meta_data)

        if to_json == True:
            _o_dict=json.dumps(_o_dict)
        return   _o_dict

    @classmethod
    def decode(cls,_o_dict,use_binary=False):

        encoded_name = _o_dict['name']
        encoded_meta_data = _o_dict['meta_data']
        if use_binary is True:
            t_rec = base64.b64decode(_o_dict['binary'])
            try:
                t_rec = pickle.loads(t_rec)
            except:
                t_rec= pickle.loads(t_rec,encoding='latin')

        else:
            t_rec = ascii.read(_o_dict['ascii'])

        return cls(t_rec,name=encoded_name,meta_data=encoded_meta_data)



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



        layout = row(
            self.fig
        )
        #curdoc().add_root(layout)


        #show(layout)

        #script, div = components(layout)

        #print ('script',script)
        #print ('div',div)

        #html_dict = {}
        #html_dict['script'] = script
        #html_dict['div'] = div

        return components(layout)




@micro_service.route('/test-bokeh')
def index():
    # Determine the selected feature

    p=ScatterPlot(800,400)
    p.add_line([0,1],[0,1])

    script, div = p.get_html_draw()
    # Create the plot

    return render_template("plot.html", script=script, div=div)



@micro_service.errorhandler(APIerror)
def handle_api_error(error):
    #print('handle_api_error 1')
    response = jsonify(error.to_dict())
    #response.json()['error message'] = error
    response.status_code = error.status_code

    return response

@api.errorhandler(APIerror)
def handle_api_error(error):
    #print('handle_api_error 2')
    response = jsonify(error.to_dict())
    response.json()['error message']=error
    response.status_code = error.status_code

    return response




@ns_conf.route('/search-by-name')
class SearchName(Resource):
    @api.doc(responses={410: ''}, params={'target_name': 'the source name'})
    def get(self):
        """
        returns the file list for a given source
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('target_name', required=True, help="the name of the source",type=str)
        api_args = api_parser.parse_args()
        target_name = api_args['target_name']
        config = micro_service.config.get('conf')
        print('target_name', target_name)
        #TODO make this walk through directories
        #TODO and put root_file into a method/function
        catalog_file=os.path.join(config.data_root_path,config.catalog_file)

        try:
            with open(catalog_file) as f:
                data = yaml.load(f,Loader=yaml.FullLoader)


            target_list=[]
            print('target_name',target_name)
            for key, value in data[config.source_name_field].items():
                print('key, value', key, value)
                if value is not None:
                    print('target_list', target_list)
                    target_list.extend([key for f in value.split(';') if f.strip().lower()==target_name.lower()])
                    print('target_list', target_list)

            target_list=[n.replace('Tpname','target').replace('Taname','target') for n in target_list]
            print('target_list',target_list)
            _o_dict = {}
            _o_dict['MWL_files'] = [n for n in data[config.MW_file_kw] if any(t in n for t in target_list)]
            _o_dict['MAGIC_files'] = [n for n in data[config.MAGIC_file_kw] if any(t in n for t in target_list)]
            #print(_o_dict)
            #print('go')
            return jsonify(_o_dict)
        except Exception as e:
            print(e)
            raise APIerror('table file is empty/corrupted or missing: %s' % e, status_code=410)


@ns_conf.route('/targets')
class Targets(Resource):
    @api.doc(responses={410: ''},)
    def get(self):
        """
        returns the list of sources
        """
        config = micro_service.config.get('conf')
        # TODO make this walk through directories
        # TODO and put root_file into a method/function
        catalog_file = os.path.join(config.data_root_path, config.catalog_file)
        try:
            with open(catalog_file) as f:
                data = yaml.load(f,Loader=yaml.FullLoader)

            return jsonify(data[config.source_name_field])
        except Exception as e:
            print(e)
            raise APIerror('table catalog is empty/corrupted or missing: %s' % e, status_code=410)


@ns_conf.route('/catalog')
class Catalog(Resource):
    @api.doc(responses={410: 'Catalog file is empty/corrupted or missing'})
    def get(self):
        """
        returns the catalog
        """
        config = micro_service.config.get('conf')
        # TODO make this walk through directories
        # TODO and put root_file into a method/function
        catalog_file = os.path.join(config.data_root_path, config.catalog_file)
        try:
            with open(catalog_file) as f:
                data = yaml.load(f,Loader=yaml.FullLoader)

            #_o_dict = json.dumps(data,sort_keys=False)
            _o_dict=dict(catalog=data)
            #print(_o_dict)
            return jsonify(_o_dict)
        except Exception as e:
            print(e)
            raise APIerror('Catalog file is empty/corrupted or missing: %s'%e, status_code=410)


@ns_conf.route('/get-table')
class APITable(Resource):
    @api.doc(responses={410: 'table file is empty/corrupted or missing'}, params={'file_name': 'the file name'})
    def get(self):
        """
        returns the astropy table
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('file_name', required=True, help="the name of the file",type=str)
        api_args = api_parser.parse_args()
        file_name = api_args['file_name']
        print('file_name',file_name)
        try:
            #api_args = api_parser.parse_args()
            #file_name = api_args['file_name']
            #print('file_name', file_name)
            config = micro_service.config.get('conf')
            # TODO make this walk through directories
            # TODO and put root_file into a method/function
            file_path = get_path(file_name)
            table = MAGICTable.from_file(file_path=file_path, format='ascii', name='MAGIC TABLE')
            _o_dict = {}
            _o_dict['astropy_table'] = table.encode(use_binary=False)
            _o_dict = json.dumps(_o_dict)
        except Exception as e:
            #print('qui',e)
            raise APIerror('table file is empty/corrupted or missing: %s'%e, status_code=410)

        return jsonify(_o_dict)


@ns_conf.route('/get-html-table')
class APITableHtml(Resource):
    @api.doc(responses={410: 'table file is empty/corrupted or missing'}, params={'file_name': 'the file name'})
    def get(self):
        """
        returns the html view of an astropy table
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('file_name', required=True, help="the name of the file",type=str)
        api_args = api_parser.parse_args()
        file_name = api_args['file_name']
        print('file_name',file_name)
        try:
            #api_args = api_parser.parse_args()
            #file_name = api_args['file_name']
            #print('file_name', file_name)
            # TODO make this walk through directories
            # TODO and put root_file into a method/function
            file_path = get_path(file_name)
            table = MAGICTable.from_file(file_path=file_path, format='ascii', name='MAGIC TABLE').table
            #_o_dict = {}
            #_o_dict['astropy_table'] = t.encode(use_binary=False)
            #_o_dict = json.dumps(_o_dict)
        except Exception as e:
            #print('qui',e)
            raise APIerror('table file is empty/corrupted or missing: %s'%e, status_code=410)
        #return output_html(t.table.show_in_notebook().data,200)
        return output_html(table.show_in_browser(jsviewer=True),200)


@ns_conf.route('/plot-sed')
class APIPlotSED(Resource):
    @api.doc(responses={410: 'table file is empty/corrupted or missing'}, params={'file_name': 'the file name'})
    def get(self):
        """
        returns the plot for a SED table
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('file_name', required=True, help="the name of the file", type=str)
        api_args = api_parser.parse_args()
        file_name = api_args['file_name']

        try:
            file_path = get_path(file_name)
            sed_table = MAGICTable.from_file(file_path=file_path, format='ascii', name='MAGIC TABLE').table
            name = ''
            if 'Source' in sed_table.meta:
                name = sed_table.meta['Source']

            #sed_plot = DataPlot()

            #sed_plot.add_data_plot(x=sed_table['freq'], y=sed_table['nufnu'],
            #                       dx=[sed_table['freq_elo'], sed_table['freq_eup']],
            #                       dy=[sed_table['nufnu_elo'], sed_table['nufnu_eup']], label=name)

            #sed_plot.ax.set_ylabel(sed_table['nufnu'].unit)
            #sed_plot.ax.set_xlabel(sed_table['freq'].unit)
            #sed_plot.ax.grid()
            #buf = BytesIO()
            #sed_plot.fig.savefig(buf, format="png")
            #data = base64.b64encode(buf.getbuffer()).decode("ascii")

            sp1 = ScatterPlot(w=800, h=600, x_label=str(sed_table['freq'].unit), y_label=str(sed_table['nufnu'].unit),
                              y_axis_type='log', x_axis_type='log')

            sp1.add_errorbar(sed_table['freq'], sed_table['nufnu'], yerr=sed_table['nufnu_elo'], xerr=sed_table['freq_elo'])

            script, div = sp1.get_html_draw()


            return output_html(render_template("plot.html", script=script, div=div),200)


        except Exception as e:
            #print('qui',e)
            raise APIerror('problem im producing sedplot: %s'%e, status_code=410)

        #return output_html(f"<img src='data:image/png;base64,{data}'/>", 200)


@ns_conf.route('/plot-lc')
class APIPlotLC(Resource):
    @api.doc(responses={410: 'table file is empty/corrupted or missing'}, params={'file_name': 'the file name'})
    def get(self):
        """
         returns the plot for a LC table
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('file_name', required=True, help="the name of the file", type=str)
        api_args = api_parser.parse_args()
        file_name = api_args['file_name']

        try:
            file_path = get_path(file_name)
            lc_table = MAGICTable.from_file(file_path=file_path, format='ascii', name='MAGIC TABLE').table
            name = ''
            if 'Source' in lc_table.meta:
                name = lc_table.meta['Source']

            #lc_plot = DataPlot()

            #lc_plot.add_data_plot(x=lc_table['tstart'], y=lc_table['nufnu'],
            #                      dy=[lc_table['nufnu_elo'], lc_table['nufnu_eup']], label=name, loglog=False)
            #lc_plot.ax.set_ylabel(lc_table['nufnu'].unit)
            #lc_plot.ax.set_xlabel(lc_table['tstart'].unit)
            #lc_plot.ax.grid()
            #buf = BytesIO()
            #lc_plot.fig.savefig(buf, format="png")
            #data = base64.b64encode(buf.getbuffer()).decode("ascii")

            lc = ScatterPlot(w=800, h=600, x_label=str(lc_table['tstart'].unit), y_label=str(lc_table['nufnu'].unit))

            lc.add_errorbar(lc_table['tstart'], lc_table['nufnu'], yerr=lc_table['nufnu_eup'])

            script, div = lc.get_html_draw()

            return output_html(render_template("plot.html", script=script, div=div), 200)

        except Exception as e:
            #print('qui',e)
            raise APIerror('problem im producing sedplot: %s'%e, status_code=410)

        #plugins.connect(lc_plot.fig, plugins.MousePosition(fontsize=14))

        #print('ciccio')
        #mpld3.show()
        #return  output_html(render_template('plot_mpld3.html', plot=mpld3.fig_to_html(lc_plot.fig)),200)
        #return  mpld3.fig_to_html(lc_plot.fig)

        return output_html(f"<img src='data:image/png;base64,{data}'/>", 200)

def run_micro_service(conf,debug=False,threaded=False):

    #micro_service.config_dir.from_pyfile('config_dir.py')
    micro_service.config['conf'] = conf
    micro_service.config["JSON_SORT_KEYS"] = False

    print(micro_service.config,micro_service.config['conf'])


    micro_service.run(host=conf.url,port=conf.port,debug=debug,threaded=threaded)



