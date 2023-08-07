.. _analysis:

Analysis and visualization
===========================

We have developed a python package that contains a set of functions and a web-based app for analysis of FED3Bandit data and  for data visualization.
For the API, please see the :ref:`api` section. On the :ref:`Analysis pipelines` section you can find examples on how to 
use these functions to analyze and visualize FED3Bandit data.

.. _install-package:

Installation
-------------

Detailed instructions
#######################
These instructions assume that you are using the Anaconda distribution of python:

1. Open Anaconda prompt (Windows) or terminal (MacOS/Linxux)
2. Type: ``conda create --name fed3bandit python=3.10``. This creates a brand new conda environment where ``fed3bandit`` will be installed
3. When prompt outputs: ``Proceed ([y]/n)?`` type ``y``
4. When everything is finished type: ``conda activate fed3bandit``. This will activate the ``fed3bandit`` environment. You should see ``(fed3bandit)`` in the new line.
5. Type: ``conda install pip`` and type ``y`` if prompted
6. Type: ``pip install fed3bandit`` and type ``y`` if prompted.

Installation using pip
#######################
The fed3 python package can be installed using pip. 

``pip install fed3bandit``

Testing the Installation
#########################
To test the installation, open a new python file, and execute the following code.

.. code-block:: python

      import fed3bandit as f3b
      import matplotlib.pyplot as plt
      import pandas as pd
      import numpy as np

      #load sample data
      sample_data = f3b.load_sampledata()

      #Get the true left reward probability as well as the mouse estimation
      true_left = f3b.left_probs(sample_data, offset=5)
      mouse_left = f3b.binned_paction(sample_data, window=5)

      #Plotting
      fig, ax = plt.subplots(figsize=(12,4))
      ax.plot(np.arange(len(left_probs)), left_probs, c="red", linewidth=3)
      ax.plot(np.arange(len(left_probs)), binned_actions, linewidth=3)
      ax.set_ylabel("P(Left)")
      ax.set_xlabel("Events")
      plt.show()

If everything works correctly, this should be the ouptut:

.. image:: /_static/sample_behavior_output.png



Testing the web-app
#####################
To run and test the web-app please see :ref:`fed3-app`


Reference
-------------

.. toctree::
   :maxdepth: 1
   
   fed3live_api
   web_app
   
   