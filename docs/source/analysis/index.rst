.. _analysis:

Analysis and visualization
===========================

We have developed a python package that contains a set of functions and a web-based app for analysis of FED3Bandit data and  for data visualization.
For the reference of the functions, please see the :ref:`api` section. On the :ref:`Analysis pipelines` section you can find examples on how to 
use these functions to analyze and visualize FED3Bandit data.

Please see :ref:`fed3-app` section for instructions on how to run and use the web-based app.

.. _install-package:

Installation
-------------

The fed3 python package can be installed using pip. 

``pip install fed3bandit``


Detailed instructions
#######################
These instructions assume that you are using the Anaconda distribution of python:

1. Open Anaconda prompt (Windows) or terminal (MacOS/Linxux)
2. Type: ``conda create --name fed3bandit python=3.10``. This creates a brand new conda environment where ``fed3bandit`` will be installed
3. When prompt outputs: ``Proceed ([y]/n)?`` type ``y``
4. When everything is finished type: ``conda activate fed3bandit``. This will activate the ``fed3bandit`` environment. You should see ``(fed3bandit)`` in the new line.
5. Type: ``conda install pip`` and type ``y`` if prompted
6. Type: ``pip install fed3bandit`` and type ``y`` if prompted.

That's it!

Reference
-------------

.. toctree::
   :maxdepth: 1
   
   fed3live_api
   web_app
   
   