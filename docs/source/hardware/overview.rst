Overview
===============================

FED3Bandit is an implementation of a 2-armed bandit task that uses a FED3 device. FED3Bandit uses FED3, which means it is highly customizible, 
it can be used in rodents home-cage, and requires minimal supervision (food and battery level checks every few days). In this page we first provide a brief introduction
of a 2-armed bandit task and we then describe the features that FED3Bandit has and the ways in which it can be customized.

Two-armed bandit task
-------------------------
A two-armed bandit task is a special case of the k-armed bandit problem. It consists of the SOMETHING of two choices that are each associated to a probability of
receiving a reward. Let these two choices be "Left" and "Right". The reward probabilities of Left and Right can be fixed, or come from a probability distribution,
and may be independent from each other. 

SCHEMATIC OF BANDIT BASICS

Additionally, the reward probabilities of Left and Right may change upon the SOMETHING of a condition. In this case, the task is called *nonstationary*. A special
case of *nonstationary* bandit task it the *restless two-armed bandit task* where reward probabilities may change after each choice.

SCHEMATIC OF NONSTATIONARY BANDIT TASK

Here are some examples of conditions that may be used to trigger the change in reward probabilities:
* After n reward
* After m consecutive choices in the higher probability side
* After every choice


FED3Bandit
-----------
FED3Bandit is an implementation of the two-armed bandit task using the FED3 device. It is designed for home-cage training. You can find more information about FED3 here.
In this section we will describe the FED3 features as they pertain to FED3Bandit.

