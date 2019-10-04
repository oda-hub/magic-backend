
from __future__ import absolute_import, division, print_function

from builtins import (open, str, range,
                      object)

from oda_api.data_products import AstropyTable
from flask import Flask, jsonify, abort,request
from flask_restplus import Api, Resource,reqparse

from astropy.table import Table
from flask.json import JSONEncoder
import numpy as np
import json
import yaml
import pickle
import base64
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO



micro_service = Flask("micro_service")
api= Api(app=micro_service, version='1.0', title='MAGIC back-end API',
    description='API to extract data for MAGIC Telescope\n Author: Andrea Tramacere',)
ns_conf = api.namespace('api/v1.0/magic', description='Conference operations')

parser = reqparse.RequestParser()
parser.add_argument('file_name')

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



class APIerror(Exception):

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error_message'] = self.message
        return rv




class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return list(obj)
        return JSONEncoder.default(self, obj)


app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

@micro_service.errorhandler(APIerror)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@ns_conf.route('/catalog')
@api.doc()
class Catalog(Resource):
    @api.doc(responses={410: 'catalog file is empty/corrupted or missing'})
    def get(self):
        """
        returns the catalog
        """
        try:
            with open('MAGIC_data/data/19e/magic_19e.yaml') as f:
                data = yaml.load(f)

            _o_dict = json.dumps(data,sort_keys=False)
            print(_o_dict)
            return jsonify(_o_dict)
        except Exception as e:
            raise APIerror('table file is empty/corrupted or missing', status_code=410)

@ns_conf.route('/data')
@api.doc(responses={410: 'table file is empty/corrupted or missing'}, params={'file_name': 'the file name'})
class Data(Resource):
    def get(self):
        """
        returns the astropy table
        """



        try:
            args = parser.parse_args()
            file_name = args['file_name']
            print('file_name', file_name)
            t = AstropyTable(Table.read('MAGIC_data/data/19e/%s'%file_name, format='ascii'),name='MAGIC TABLE')
            _o_dict = {}
            _o_dict['astropy_table'] = t.encode(use_binary=False)
            _o_dict = json.dumps(_o_dict)
        except Exception as e:
            raise APIerror('table file is empty/corrupted or missing', status_code=410)



        return jsonify(_o_dict)


#api.add_resource(Catalog, '/api/v1.0/magic/get-catalog')
#api.add_resource(Data, '/api/v1.0/magic/get-data')

if __name__ == '__main__':
    micro_service.config.from_pyfile('config.py')
    print(micro_service.config)
    micro_service.run(host="0.0.0.0",port=micro_service.config['PORT'])
