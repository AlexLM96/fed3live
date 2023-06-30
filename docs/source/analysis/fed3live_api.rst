.. _fed3live:

fed3bandit python package
==========================

Fed3bandit is a python package for the analysis of the FED3Bandit task. It consists of funtions for the
processing and analysis of FED3Bandit data. On this page you can find the API documentation of these functions.
On the :ref:`Analysis pipelines` section you can find examples on how to use these functions to analyze and 
visualize FED3Bandit data in multiple ways.

Installation
-------------

FED3Bandit python package can be installed using pip. 

``pip install fed3bandit``

Summary of functions
---------------------

.. automodule:: fed3live.fed3live
   
   .. rubric:: Functions

   .. autosummary::
   
      load_sampledata
      filter_data
      binned_paction
      count_pellets
      count_pokes
      pokes_per_pellet
      poke_accuracy
      reversal_peh
      win_stay
      lose_shift
      side_prewards
      side_nrewards
      create_X
      logit_regr
   

API Reference
--------------

.. automodule:: fed3live.fed3live
   :members:
   :show-inheritance:
   :member-order: bysource

Extending fed3live
-------------------

FED3Bandit is a actively being developed. We will keep adding more analysis features.
If you have any request, please open an issue on GitHub and we will try to implement it 
in a future release.