
from __future__ import absolute_import, division, print_function

from builtins import (open, str, range,
                      object)

from flask import Flask, jsonify, abort,request,render_template,Response,make_response
from flask_restplus import Api, Resource,reqparse
from flask.json import JSONEncoder

from astropy.table import Table
import json
import yaml
import pickle
import glob
import os
import  numpy as np


import base64
from io import BytesIO
from .plot_tools import ScatterPlot
from .data_tools import MAGICTable,get_targets_dic

from magic_data_server import conf_dir


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            print('hi')
            return list(obj)

        return JSONEncoder.default(self, obj)

template_dir =os.path.abspath(os.path.dirname(__file__))+'/templates'
static_dir=os.path.abspath(os.path.dirname(__file__))+'/static'

micro_service = Flask("micro_service",template_folder=template_dir,static_folder=static_dir)
micro_service.json_encoder = CustomJSONEncoder

api= Api(app=micro_service, version='1.0', title='MAGIC back-end API',
    description='API to extract data for MAGIC Telescope\n Author: Andrea Tramacere',)
ns_conf = api.namespace('api/v1.0/magic', description='data access')



def set_paper_id(paper_id):
    catalog_dir = paper_id
    paper_id = catalog_dir.split('_')[0]

    return paper_id

def get_catalog_path(paper_id):
    config = micro_service.config.get('conf')

    catalog_dir =paper_id
    if paper_id is not None:
        paper_id = set_paper_id(paper_id)

        catalog_file_name = config.catalog_file_prefix + paper_id + config.catalog_file_type
        catalog_file_path = [os.path.join(config.data_root_path, catalog_dir, catalog_file_name)]
        catalog_file_dir = os.path.join(config.data_root_path, catalog_dir)
    else:
        catalog_file_name=None



    if catalog_file_name is None:
        p=os.path.join(config.data_root_path,'*','%s*%s'%( config.catalog_file_prefix,config.catalog_file_type))
        print('p',p)
        catalog_file_path=glob.glob(p)
        catalog_file_dir=None

    return catalog_file_path,catalog_file_dir

def get_file_path(paper_id,file_name):

    config = micro_service.config.get('conf')
    file_path = os.path.join(config.data_root_path, paper_id, file_name)
    return file_path

def get_papers_collection():
    config = micro_service.config.get('conf')
    return os.listdir(config.data_root_path)

def output_html(data, code, headers=None):
    resp = Response(data, mimetype='text/html', headers=headers)
    resp.status_code = code
    return resp

class Configurer(object):
    def __init__(self, cfg_dict):
        self._valid=['port','url','data_root_path','catalog_file_prefix','catalog_file_type','source_name_field','MW_file_kw','MAGIC_file_kw']
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

class APP(Exception):
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message

        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        print('APP Error Message',message)




@micro_service.errorhandler(APP)
def handle_app_error(error):
    return 'bad request! %s'%error.message, 400

@micro_service.route('/index')
def index():
    return render_template("index.html")

def get_pars():
    p_dict=None
    if request.method == 'POST':
        p_dict= request.form

    if request.method == 'GET':
        p_dict = request.args.to_dict()

    return p_dict




@micro_service.route('/search-name',methods=['GET', 'POST'])
def search_name():
    c=SearchName()
    files_dict = c.get().json
    file_type=[]
    file_name_list=[]

    for k in files_dict.keys():
        file_type.append('%s:'%(k))
        file_name_list.append(files_dict[k])
        print(files_dict[k])
    return render_template("index.html",file_names=zip(file_type,file_name_list))


@micro_service.route('/show-papers',methods=['GET', 'POST'])
def show_papers():
    c = Papers()
    papers_id_list = c.get().json
    s = []
    n = []
    print(papers_id_list)
    for ID,p in enumerate(papers_id_list):
        print(ID,p)
        s.append('id_%02d :'%ID)
        n.append(' %s' %p)
    return render_template("index.html",paper_ids=zip(s,n))

@micro_service.route('/show-targets',methods=['GET', 'POST'])
def show_targets():
    c = Targets()
    targets = get_targets_dic(c.get().json)
    s = []
    n = []
    for k in targets.keys():
        s.append('%s :'%k)
        n.append(' %s' % (targets[k][0]))
    return render_template("index.html",targets=zip(s,n))

@micro_service.route('/plot-target',methods=['GET', 'POST'])
def plot_target():
    script = None
    div = None

    p_dict=get_pars()
    #if request.method == 'POST':
    file_name = p_dict['file_name']
    #paper_id=p_dict['paper_id']

    try:
        if 'sed' in file_name:
            c=APIPlotSED()

        if 'lc' in file_name:
            c = APIPlotLC()

        script, div = c.get(render=False)
        resp = make_response('{"test": "ok"}')
        resp.headers['Content-Type'] = "text/html"
        if 'render' in p_dict.keys():
            return render_template("plot.html", script=script, div=div, )
        else:
            return Response((script, div), content_type='text/html')
        #return make_response(script=script, div=div)
        #return render_template("index.html", script=script, div=div,)
    except Exception as e:
        print(e)
        raise APP('table file is empty/corrupted or missing: %s' % e, status_code=410)



@micro_service.errorhandler(APIerror)
def handle_api_error(error):
    #print('handle_api_error 2')
    response = jsonify(error.to_dict())
    #response.json()['error message']=error
    response.status_code = error.status_code
    return response

@api.errorhandler(APIerror)
def handle_api_error(error):
    #print('handle_api_error 2')
    response = jsonify(error.to_dict())
    #response.json()['error message']=error
    response.status_code = error.status_code

    return response



@ns_conf.route('/test-connection')
class Papers(Resource):
    @api.doc(responses={410: ''},)
    def get(self):
        """
        returns the list of paper ids
        """
        config = micro_service.config.get('conf')
        try:
            return jsonify(['connection OK'])
        except Exception as e:
            print(e)
            raise APIerror('NO connection', status_code=410)


@ns_conf.route('/paper_ids')
class Papers(Resource):
    @api.doc(responses={410: ''},)
    def get(self):
        """
        returns the list of paper ids
        """
        config = micro_service.config.get('conf')
        try:
            papers_ids_list = os.listdir(config.data_root_path)

            return jsonify(papers_ids_list)
        except Exception as e:
            print(e)
            raise APIerror('no paper folder found: %s' % e, status_code=410)

@ns_conf.route('/catalog')
class Catalog(Resource):
    @api.doc(responses={410: 'Catalog file is empty/corrupted or missing'},params={'paper_id':'the paper id'})
    def get(self):
        """
        returns the catalog
        """
        config = micro_service.config.get('conf')
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('paper_id', required=True, help="the id of the paper", type=str)

        api_args = api_parser.parse_args()

        paper_id=api_args['paper_id']

        catalog_file_path,catalog_file_dir=get_catalog_path(paper_id)
        #print('-->',catalog_file_path,catalog_file_dir)
        # TODO make this walk through directories
        # TODO and put root_file into a method/function

        _o_dict={}
        data=[]
        try:
            for cf in catalog_file_path:
                with open(cf) as f:
                    data.extend([yaml.load(f,Loader=yaml.FullLoader)])

            #_o_dict = json.dumps(data,sort_keys=False)
            _o_dict=dict(catalog=data)
            #print('-->',_o_dict,data)
            return jsonify(_o_dict)
        except Exception as e:
            print(e)
            raise APIerror('Catalog file is empty/corrupted or missing: %s'%e, status_code=410)


@ns_conf.route('/targets')
class Targets(Resource):
    @api.doc(responses={410: ''},params={'paper_id':'the paper id'})
    def get(self):
        """
        returns the list of sources
        """
        config = micro_service.config.get('conf')
        #print('--> config',config)
        # TODO make this walk through directories
        # TODO and put root_file into a method/function
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('paper_id', required=True, help="the id of the paper", type=str)

        api_args = api_parser.parse_args()

        paper_id = api_args['paper_id']

        catalog_file_path,catalog_file_dir = get_catalog_path(paper_id)
        data=[]
        try:
            for cf in catalog_file_path:
                with open(cf) as f:
                    _d=yaml.load(f,Loader=yaml.FullLoader)
                    print('_d[config.source_name_field]',_d[config.source_name_field])
                    data.extend([_d[config.source_name_field]])

            return jsonify(data)
        except Exception as e:
            print(e)
            raise APIerror('table catalog is empty/corrupted or missing: %s' % e, status_code=410)


@ns_conf.route('/search-by-name')
class SearchName(Resource):
    @api.doc(responses={410: ''}, params={'target_name': 'the source name','paper_id':'the paper id','get_products': 'bool flag to get table data'})
    def get(self):
        """
        returns the file list for a given source
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('target_name', required=True, help="the name of the source",type=str)
        api_parser.add_argument('paper_id', required=False, help="the id of the paper", type=str)
        api_parser.add_argument('get_products', required=False, help="bool flag to get table data", type=bool)
        api_args = api_parser.parse_args()
        target_name = api_args['target_name']
        paper_id= api_args['paper_id']
        #print('target_name', target_name)
        config = micro_service.config.get('conf')
        #print('target_name', target_name)
        #TODO make this walk through directories
        #TODO and put root_file into a method/function
        if paper_id is not None:
            if paper_id.strip()=='':
                paper_id =None

        catalog_file_path,catalog_file_dir = get_catalog_path(paper_id)
        print('->start')
        print('->target_name', target_name)
        print('->paper_id', paper_id)
        print('->catalog_file_path',catalog_file_path)
        _o_dict = {}
        _o_dict['src_name'] = target_name
        _o_dict['src_aliases'] = []
        _prod_dict = lambda src_name,src_aliases,file, paper_id, table: {'src_name': src_name,
                                                                         'src_aliases': src_aliases,
                                                                         'file': file,
                                                                         'paper_id': paper_id,
                                                                         'astropy_table' : table}
        _o_dict['MWL_files']={}
        _o_dict['MAGIC_files']={}
        _p_id_mwf=0
        _p_id_mgf=0
        try:
            for cf in catalog_file_path:
                with open(cf) as f:
                    data = yaml.load(f,Loader=yaml.FullLoader)

                target_list=[]
                for key, value in data[config.source_name_field].items():
                    if value is not None:

                        target_list.extend([key for f in value.split(';') if f.strip().lower()==target_name.lower()])

                target_list = [n.replace('Taname', 'Tpname') for n in target_list]
                #for t in target_list:
                #    _o_dict['src_name'].append(data[config.source_name_field][t])

                target_list = [n.replace('Tpname', 'Taname') for n in target_list]
                for t in target_list:
                    _o_dict['src_aliases'].append(data[config.source_name_field][t])

                if paper_id is None:
                    _current_paper_id=os.path.basename(os.path.dirname(cf))
                else:
                    _current_paper_id=paper_id

                if len(target_list)>0:
                    mw_files=[]
                    if config.MW_file_kw in data.keys():
                        mw_files=data[config.MW_file_kw]

                    magic_files=[]
                    if config.MAGIC_file_kw in data.keys():
                        magic_files=data[config.MAGIC_file_kw]

                    src_name=_o_dict['src_name']
                    for n in mw_files:
                        _t = MAGICTable.from_file(file_path=get_file_path(_current_paper_id, n), format='ascii', name='MAGIC TABLE')

                        if src_name in _t.table['srcname']:
                            p_dict=_prod_dict(src_name,_o_dict['src_aliases'][-1],n,_current_paper_id, _t.encode(use_binary=False))
                            _o_dict['MWL_files']['prod_id_%d'%_p_id_mwf]=p_dict
                            _p_id_mwf+=1
                    for n in magic_files:

                        _t = MAGICTable.from_file(file_path=get_file_path(_current_paper_id, n), format='ascii', name='MAGIC TABLE')
                        if src_name in _t.table['srcname']:
                            p_dict = _prod_dict(src_name,_o_dict['src_aliases'][-1],n, _current_paper_id,  _t.encode(use_binary=False))
                            _o_dict['MAGIC_files']['prod_id_%d'%_p_id_mgf]=p_dict
                            _p_id_mgf += 1
            _o_dict = json.dumps(_o_dict)
            return jsonify(_o_dict)

        except Exception as e:
            print(e)
            raise APIerror('table file is empty/corrupted or missing: %s' % e, status_code=410)






@ns_conf.route('/get-table')
class APITable(Resource):
    @api.doc(responses={410: 'table file is empty/corrupted or missing'}, params={'file_name': 'the file name','paper_id':'the paper id'})
    def get(self):
        """
        returns the astropy table
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('src_name', required=False, help="src name", type=str)
        api_parser.add_argument('file_name', required=True, help="the name of the file",type=str)
        api_parser.add_argument('paper_id', required=True, help="the paper id", type=str)
        api_args = api_parser.parse_args()
        file_name = api_args['file_name']
        paper_id = api_args['paper_id']
        try:
            #api_args = api_parser.parse_args()
            #file_name = api_args['file_name']
            config = micro_service.config.get('conf')
            # TODO make this walk through directories
            # TODO and put root_file into a method/function
            file_path = get_file_path(paper_id,file_name)
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
    @api.doc(responses={410: 'table file is empty/corrupted or missing'}, params={'file_name': 'the file name','paper_id':'the paper id'})
    def get(self):
        """
        returns the html view of an astropy table
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('file_name', required=True, help="the name of the file",type=str)
        api_parser.add_argument('paper_id', required=True, help="the paper id", type=str)
        api_args = api_parser.parse_args()
        file_name = api_args['file_name']
        paper_id = api_args['paper_id']
        try:
            #api_args = api_parser.parse_args()
            #file_name = api_args['file_name']
            #print('file_name', file_name)
            # TODO make this walk through directories
            # TODO and put root_file into a method/function
            file_path = get_file_path(paper_id, file_name)
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
    @api.doc(responses={410: 'table file is empty/corrupted or missing'}, params={'file_name': 'the file name','paper_id':'the paper id'})
    def get(self,render=True):
        """
        returns the plot for a SED table
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('file_name', required=True, help="the name of the file", type=str)
        api_parser.add_argument('paper_id', required=True, help="the paper id", type=str)
        api_args = api_parser.parse_args()
        file_name = api_args['file_name']
        paper_id = api_args['paper_id']

        try:
            file_path = get_file_path(paper_id, file_name)
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

            #if 'energy' in sed_table.colnames:
            #sed_table=sed_table['srcname']==
            x=sed_table['en']
            #elif 'freq' in sed_table.colnames:
            #    x=sed_table['freq']
             #   dx=sed_table['freq_elo']
            #else:
            #    raise APIerror('problem im producing sedplot, x axis names not valid:, status_code=410')
            #print(x, sed_table['nufnu'], dx, sed_table['nufnu_elo'])

            dx = [sed_table['en_wlo'], sed_table['en_wup']]
            dy = [sed_table['nufnu_elo'], sed_table['nufnu_eup']]

            sp1 = ScatterPlot(w=600, h=400, x_label=str(x.unit), y_label=str(sed_table['nufnu'].unit),
                              y_axis_type='log', x_axis_type='log',title=name)

            if dx is None:
                dx = np.zeros((2,len(x)))
            else:
                dx = np.fabs(x - dx)

            if dy is None:
                dy = np.zeros(len(sed_table['nufnu']))
            else:
                dy = np.fabs(sed_table['nufnu'] - dy)

            sp1.add_errorbar(x, sed_table['nufnu'],xerr=dx,yerr=dy,dataformat=sed_table['dataformat'])

            script, div = sp1.get_html_draw()

            if render is True:
                return output_html(render_template("plot.html", script=script, div=div),200)
            else:
                return script, div


        except Exception as e:
            #print('qui',e)
            raise APIerror('problem im producing sedplot: %s'%e, status_code=410)

        #return output_html(f"<img src='data:image/png;base64,{data}'/>", 200)


@ns_conf.route('/plot-lc')
class APIPlotLC(Resource):
    @api.doc(responses={410: 'table file is empty/corrupted or missing'}, params={'file_name': 'the file name','paper_id':'the paper id'})
    def get(self,render=True):
        """
         returns the plot for a LC table
        """
        api_parser = reqparse.RequestParser()
        api_parser.add_argument('file_name', required=True, help="the name of the file", type=str)
        api_parser.add_argument('paper_id', required=True, help="the paper id", type=str)
        api_args = api_parser.parse_args()
        file_name = api_args['file_name']
        paper_id=api_args['paper_id']
        try:
            file_path = get_file_path(paper_id,file_name)
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

            lc = ScatterPlot(w=600, h=400, x_label=str(lc_table['tstart'].unit), y_label=str(lc_table['nufnu'].unit),title=name)

            lc.add_errorbar(lc_table['tstart'], lc_table['nufnu'], yerr=lc_table['nufnu_eup'])

            script, div = lc.get_html_draw()

            if render is True:
                return output_html(render_template("plot.html", script=script, div=div),200)
            else:
                return script, div

        except Exception as e:
            #print('qui',e)
            raise APIerror('problem im producing sedplot: %s'%e, status_code=410)

        #plugins.connect(lc_plot.fig, plugins.MousePosition(fontsize=14))

        #print('ciccio')
        #mpld3.show()
        #return  output_html(render_template('plot_mpld3.html', plot=mpld3.fig_to_html(lc_plot.fig)),200)
        #return  mpld3.fig_to_html(lc_plot.fig)

        #return output_html(f"<img src='data:image/png;base64,{data}'/>", 200)

def run_micro_service(conf,debug=False,threaded=False):

    #micro_service.config_dir.from_pyfile('config_dir.py')
    micro_service.config['conf'] = conf
    micro_service.config["JSON_SORT_KEYS"] = False

    print(micro_service.config,micro_service.config['conf'])


    micro_service.run(host=conf.url,port=conf.port,debug=debug,threaded=threaded)



