Overview
===============================

FED3Bandit is an implementation of a 2-armed bandit task that uses a FED3 device. FED3Bandit uses FED3, which means 
it is highly customizible, it can be used in rodents home-cage, and requires minimal supervision 
(food and battery level checks every few days). 

In this page we first provide a brief introduction of a 2-armed bandit task and we then describe the features 
that FED3Bandit has and the ways in which it can be customized.

Two-armed bandit task
-------------------------
A two-armed bandit task is a special case of the k-armed bandit problem. It consists of the SOMETHING of 
two choices that are each associated to a probability of receiving a reward. Let these two choices be 
"Left" and "Right". The reward probabilities of Left and Right can be fixed, or they can come from a probability 
distribution, and may be independent from each other. 

SCHEMATIC OF BANDIT BASICS

Additionally, the reward probabilities of Left and Right may change upon the SOMETHING of a condition. 
In this case, the task is called *nonstationary*. A special case of *nonstationary* bandit task is
the *restless two-armed bandit task*, where reward probabilities change after each choice.

SCHEMATIC OF NONSTATIONARY BANDIT TASK

Here are some examples of conditions that may be used to trigger the change in reward probabilities:

* After n rewards deliverd
* After m consecutive choices in the higher probability port
* After every choice


FED3Bandit
-----------
FED3Bandit is an implementation of the two-armed bandit task that that usesthe FED3 device.In this section we will describe the FED3 features as they pertain to FED3Bandit.

FED3 has two nose pokes, which are used in FED3Bandit as the two "arms". Additionally, FED3 has a well through which food pellets are dispensed. FED3Bandit, thus, uses
nose pokes as choices, and food pellets as rewards. 

PHOTO OF FED

To set up the bandit task, FED3 uses the Arduino programming language. There is an Arduino FED3 library that automates all the code needed to communicate with the FED3 hardware
and wraps into easy-to-use functions. Additionally, the FED3 library has examples, including bandit task examples, that are ready to be used. Alternatively, you can find 
:ref:`bandit templates` and a :ref:`tutorial` on this site.

FED3Bandit collects and logs data in the form of a CSV file into the microSD card. The :ref:`output data` section describes the specifics of the CSV file. 

For data analysis, we have developed two tools. One tool is a web-baseds application for visualization and data analysis. 