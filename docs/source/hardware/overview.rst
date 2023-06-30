Overview
===============================

FED3Bandit is an implementation of a 2-armed bandit task that uses a FED3 device. FED3Bandit uses FED3, which means 
it is highly customizible, it can be used in rodents home-cage, and requires minimal supervision 
(food and battery level checks every few days). 

In this page we first provide a brief introduction of a 2-armed bandit task and we then describe the features 
that FED3Bandit has and the ways in which it can be customized.

Two-armed bandit task
-------------------------
A two-armed bandit task is a special case of the k-armed bandit problem. It consists of an environment where there
are two choices that are each associated to a probability of receiving a reward. Let these two choices be 
"Left" and "Right". The reward probabilities of Left and Right may be fixed or come from a probability distribution,
remain constant or chenage upon a condition, and may be dependent or independent from each other.

When the reward probabilities of Left and Right change upon meeting a condition, the task is called *nonstationary*. A special case of *nonstationary* bandit task is
The *restless two-armed bandit task*, where reward probabilities change sligthly after each choice.

.. image:: /_static/stationary_bandit.svg
    :width: 500
    
|

.. image:: /_static/nonstationary_bandit.svg
    :width: 500

Here are some examples of conditions that may be used to trigger the change in reward probabilities:

* After n rewards deliverd
* After m consecutive choices in the higher probability port
* After every choice (restless bandit task)

The two-armed bandit task has become increasingly popular in neuroscience as it can probe learning behavior,
particularly learning by trial-and-error. The task is also suitable for the the use of reinforcement learning
techniques and models.

FED3Bandit
-----------
FED3Bandit is an implementation of the two-armed bandit task that that uses the FED3 device (more information 
about FED3 can be found here: :ref:`about-fed3`)In this section we will describe the FED3 features as they pertain to FED3Bandit.

FED3 has two nose pokes, which are used in FED3Bandit as the two "arms". Additionally, FED3 has a well through which food pellets are dispensed. FED3Bandit, thus, uses
nose pokes as choices, and food pellets as rewards. 

.. image:: /_static/fed3.svg
    :width: 500

|

To set up the bandit task, FED3 uses the Arduino programming language. There is an Arduino 
`FED3_Library <https://github.com/KravitzLabDevices/FED3_library>`_ that automates all the code needed to communicate with the FED3 hardware
and wraps into easy-to-use functions. Additionally, the FED3 library has examples, including bandit task examples, that are ready to be used. Alternatively, you can find 
:ref:`bandit templates` and a :ref:`tutorial` on this site.

FED3Bandit collects and logs data in the form of a CSV file into the microSD card. The :ref:`output data` section describes the specifics of the CSV file. 

For data analysis, we have developed two tools. One tool is a web-based application (fed3_app) for visualization and data analysis. fed3_app can read CSV files output from FED3Bandit
and provides visualization and analysis tools. You can find more information about how install and run fed3_app in the :ref:`fed3-app` section of this site. For data analysis fed3_app
uses the fed3live python package.

fed3live is a python package data that contains functions for analysis of FED3Bandit CSV files. You can find more information about the fed3live python package 
in the :ref:`analysis` section.