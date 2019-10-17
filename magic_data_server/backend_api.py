
from __future__ import absolute_import, division, print_function

from builtins import (open, str, range,
                      object)

from flask import Flask, jsonify, abort,request,render_template,Response
from flask_restplus import Api, Resource,reqparse

from astropy.table import Table
import json
import yaml
import pickle
import base64
import os
from collections import OrderedDict

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from magic_data_server import  conf_dir

micro_service = Flask("micro_service")

api= Api(app=micro_service, version='1.0', title='MAGIC back-end API',
    description='API to extract data for MAGIC Telescope\n Author: Andrea Tramacere',)


ns_conf = api.namespace('api/v1.0/magic', description='data access')


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


class AstropyTable(object):

    def __init__(self,table_object,name='astropy table', meta_data={}):
        self.name=name
        self.meta_data=meta_data
        self.table=table_object

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
            data_file = os.path.join(config.data_root_path, file_name)
            t = AstropyTable(Table.read(data_file, format='ascii'),name='MAGIC TABLE')
            _o_dict = {}
            _o_dict['astropy_table'] = t.encode(use_binary=False)
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
            config = micro_service.config.get('conf')
            # TODO make this walk through directories
            # TODO and put root_file into a method/function
            data_file = os.path.join(config.data_root_path, file_name)
            t = AstropyTable(Table.read(data_file, format='ascii'),name='MAGIC TABLE')
            #_o_dict = {}
            #_o_dict['astropy_table'] = t.encode(use_binary=False)
            #_o_dict = json.dumps(_o_dict)
        except Exception as e:
            #print('qui',e)
            raise APIerror('table file is empty/corrupted or missing: %s'%e, status_code=410)
        return output_html(t.table.show_in_notebook().data,200)
        #return output_html(t.table.show_in_browser(jsviewer=True),200)


def run_micro_service(conf,debug=False,threaded=False):

    #micro_service.config_dir.from_pyfile('config_dir.py')
    micro_service.config['conf'] = conf
    micro_service.config["JSON_SORT_KEYS"] = False

    print(micro_service.config,micro_service.config['conf'])


    micro_service.run(host=conf.url,port=conf.port,debug=debug,threaded=threaded)


