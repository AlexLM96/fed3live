.. _fed3-app:

fed3bandit web-app
====================

The fed3bandit web-app's goal is to provide a simple an intuitive way to visualize and analyze FED3Bandit data.

Running the app
----------------

After installing the ``fed3bandit`` package (see :ref:`install-package`) we can run the web-based app by following these steps:

1. Create a python file. To do this, open your python editor of choice (spyder, pycharm, vs code, etc) and create a new .py file. 

    * NOTE: Since  we need a .py file and not a .ipynb, Jupyter notebook cannot be used for this step.

2. Type the following:

.. code-block:: python

        import fed3bandit as f3b

        f3b.start_gui()

3. Save the file. 
4. Open Anaconda Prompt (Windows) or terminal (MacOS/Linux).
5. Activate environment where fed3bandit is installed. If you followed :ref:`install-package` instructions, you can type: ``conda activate fed3bandit``
6. Copy the location of the .py file that was saved on step 3 and type on the prompt (or terminal): ``cd HERE\GOES\LOCATION\OF\YOUR\FILE``
7. Type: ``python NAME_OF_YOUR_FILE.py``. The following message will be returned:

    .. image:: /_static/dash_address.png
        :width: 500

8. Copy the address (most of the times it will be: ``http://127.0.0.1:8050/``) and paste it on a new tab in your browser of choice.

Success!

Overview of the app
--------------------

This is wha the app should look on your browser:

.. image:: /_static/fed3bandit_app.svg
    :width: 500


In order to provide an overview of how to use the app, we have divided it into 7 elements:

1. Upload button: Here you can drag or click to load your FED3Bandit .csv files. Please note that while this button only takes .csv files,
   if other .csv files that are not the output of the FED3Bandit task are uploaded, the app may break. The Files option shows all the files
   that have been uploaded. Click to select a file.
2. Analysis options: Here you will see all the analysis options. After you select a file. Currently these options are:
    * Overview
    * Win-stay/Lose-shift
    * Reversal peh
    * Logistic wins
    * Logistic losses
3. Date and time selection: Here you can select the date and time in which the analysis will be run
4. Main panel: This is where the result of the analysis will be displayed
5. Single run button: This is where you can run the analysis for a single file. The analysis will be run on the file selected in the Files option.
6. Group analysis: Check the "Group analysis" box to enable. At least one file is required on each group to run an analysis.
   The date and time selection will update to reflect the dates/times which ALL files from both groups share. Click the "Run" button
   bello the Group 2 option to run group analysis
7. Download button: Download the analysis data that is being displayed in the main panel as a .csv. The Figure itself can be downloaded as a PNG 
   using the options from the plotting library (top right corner of the main panel).

Sample data for testing
------------------------
If you wish to test the web-app but haven't collected any data yet, you can use the sample data that is included with the ``fed3bandit`` package.
In a new python file type and execute the following:

.. code-block:: python

        import fed3bandit as f3b
        import pandas as pd

        sample_data = f3b.load_sampledata()
        sample_data.to_csv("YOUR/PATH/FILENAME.csv")

The sample data will now be saved as a .csv file in the path that was provided and can be used to test the web-app.