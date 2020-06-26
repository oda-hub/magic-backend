MAGIC backend API Documentation
==========================================
*API for MAGIC backend*

What's the license?
-------------------

magic-backend is distributed under the terms of The MIT License.

Who's responsible?
-------------------
Andrea Tramacere

ISDC Data Centre for Astrophysics, Astronomy Department of the University of Geneva, Chemin d'Ecogia 16, CH-1290 Versoix, Switzerland


Installation
------------
Clone the repository `git clone https://github.com/andreatramacere/magic-backend`

cd to the `magic-backend` directory 

* using Anaconda
     * create a virtual environment (not necessary, but suggested): 
 
       `conda create --name magic-backend python=3.7 ipython jupyter`
    
       `conda activate magic-backend`

     * `conda install -c conda-forge --file   requirements.txt`
    
* or using PIP
     * create a virtual environment (not necessary, but suggested, https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
      
     * `pip install -r requirements.txt`
     
       OR if you are using system python (deprecated)
     
     * `pip install -r requirements.txt`

* `sudo python setup.py install`

Testing 
------- 

-  cd to the `test_examples` OR copy its content to new direcotory  

-  check that the `MAGIC_data` directory is in the same directory where you run the backend 
   
   OR
   
   set the path editing the `config.yml` by setting
    - `data_root_path: MAGIC_data/data`
    

-  run 'on the command line': `run_magic_back_end.py`

   this a script installed with the package and it is available in your command line
   
- configuring port and host: edit the `config.yml` by setting:
    - `url: 0.0.0.0`
    - `port: 5001`
    - run the app passing the conf file 
    
      `run_magic_back_end.py -conf_file config.yml`
        
1) with the notebook
    
    * browse this url to get api doc `http://localhost:5001/`
        * check the backend API doc
    
    * open the `magic-test.ipynb` notebook
    
2) with the frontend

  * browse this url `http://localhost:5001/index`
   
