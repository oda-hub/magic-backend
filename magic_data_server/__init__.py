from __future__ import absolute_import, division, print_function


import pkgutil
import os

__author__ = "Andrea Tramacere"



pkg_dir = os.path.abspath(os.path.dirname(__file__))
pkg_name = os.path.basename(pkg_dir)
__all__=[]
for importer, modname, ispkg in pkgutil.walk_packages(path=[pkg_dir],
                                                      prefix=pkg_name+'.',
                                                      onerror=lambda x: None):

    if ispkg == True:
        __all__.append(modname)
    else:
        pass

conf_dir = os.environ.get("MAGIC_DATA_SERVER_CONF_DIR",
                          os.path.dirname(__file__)+'/config_dir',
                        )

print("setting config dir as", conf_dir)
