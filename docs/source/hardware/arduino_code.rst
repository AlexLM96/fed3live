Arduino Documentation
===============================

FED3Bandit uses a modified version of the FED3 arduino library. This page provides a brief description of variables and functions that are unique
to FED3Bandit or have been modified from the original library. 
You can find a more comprehensive documentation of the FED3 library `here <https://github.com/KravitzLabDevices/FED3_library/wiki>`_

Library Installation
---------------------

FED3Bandit uses a modified version of the FED3 library. You can find the source code of the FED3Bandit library `here2 <https://github.com/AlexLM96/FED3_library/tree/fed3bandit>`_.

Additionally, we will release the FED3Bandit library on the arduino library manager. 
To install the FED3Bandit library, you can follow the instructions here (NOTE, modify README on fed3bandit branch).

What's different?
------------------
This section assumes familiarity with the original FED3 library.

CSV output file
^^^^^^^^^^^^^^^^
The naming of some columns has been slightly changed to better reflect the features of the task.

==============    ===================
Original Name     FED3Bandit Name
==============    ===================
Session_Type      Prob_left
Device_Number     Prob_right
FR                Pellets_to_switch
Active_Poke       High_prob_poke
==============    ===================

Time out function
^^^^^^^^^^^^^^^^^^
The time out function has been given additional arguments that modify its behavior

.. cpp:function:: Timeout(int seconds, bool reset, bool countPokes)

    Time out function

    :param int seconds: Time out duration in seconds
    :param bool reset: Reset time out if there is a poke before time out ends
    :param bool countPokes: Counts unsuccesful pokes 
