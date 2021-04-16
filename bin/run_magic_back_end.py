#!/usr/bin/env python


# -*- encoding: utf-8 -*-
"""

"""

from __future__ import absolute_import, division, print_function

from builtins import (bytes, open, str, super, range,
                      zip, round, input, int, pow, object, map, zip)

import os
import argparse
import multiprocessing
import yaml

import gunicorn.app.base

#from gunicorn.six import iteritems

from magic_data_server.backend_api import run_micro_service, conf_micro_service

from magic_data_server import conf_dir
from magic_data_server.backend_api import Configurer




def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None, app_conf=None):
        self.options = options or {}
        self.application = app
        self.app_conf = app_conf
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])

        for key, value in config.items():
            print ('conf',key.lower(), value)
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def main(argv=None):

    black_listed_evns=['https_proxy','http_proxy']

    for envvar in black_listed_evns:
        print ('removing env variable',envvar)
        os.unsetenv(envvar)
        if envvar in os.environ.keys():
            del os.environ[envvar]

    parser = argparse.ArgumentParser()
    parser.add_argument('-conf_file', type=str, default=None)
    parser.add_argument('-use_gunicorn', action='store_true')
    parser.add_argument('-debug', action='store_true')

    args = parser.parse_args()

    conf_file = args.conf_file

    if conf_file is None:
        conf_file = os.path.join(conf_dir,'config.yml')

    conf=Configurer.from_conf_file(conf_file)

    use_gunicorn = args.use_gunicorn
    debug = args.debug

    if use_gunicorn is True:
        dispatcher_url = conf.url
        port = conf.port

        options = {
            'bind': '%s:%s' % (dispatcher_url, port),
            'workers': 2,
            'threads': 4,
            #'worker-connections': 10,
            #'k': 'gevent',
        }
        if debug:
            options['loglevel'] = 'debug'
        StandaloneApplication(conf_micro_service(conf), options).run()
    else:
        run_micro_service(conf, debug=debug, threaded=False)


if __name__ == "__main__":
    main()
