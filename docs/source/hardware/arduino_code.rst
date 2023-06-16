FED3Bandit Arduino Reference
=================================

FED3Bandit uses a modified version of the FED3 arduino library. This page provides a brief description of variables and functions that are unique
to FED3Bandit or have been modified from the original library. 
A comprehensive documentation of the FED3 library `here <https://github.com/KravitzLabDevices/FED3_library/wiki>`_

Library Installation
---------------------

FED3Bandit uses the FED3_library. You can find instructions on how to install the FED3_library `here2 <https://github.com/KravitzLabDevices/FED3_library>`_


What's different?
------------------
This section assumes familiarity with the original FED3 library.

Bandit-specific variables (API reference)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
There are variables that have been created specifically for the bandit task:

.. cpp:member:: int prob_left

The probability as a percentage of a pellet delivery after a left poke 

.. cpp:member:: int prob_right

The probability as a percentage of a pellet delivery after a right poke 

.. cpp:member:: int pelletsToSwitch

The number of pellets needed for finishing a block. However, this variable
may be used for any block switching condition

.. cpp:member:: bool allowBlockRepeat

Whether the same reward probabilities can be used for two consecutive blocks

CSV output file
^^^^^^^^^^^^^^^^
When the ``fed3.sessiontype == "Bandit"`` Two additional columns are added in the .csv output file.
Additionally, the name of two columns changes to better reflect the features of the task.

==============    ===================
Original Name     FED3Bandit Name
==============    ===================
N/A               Prob_left
N/A               Prob_right
FR                Pellets_to_switch
Active_Poke       High_prob_poke
==============    ===================
