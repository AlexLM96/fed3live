.. _tutorial:

Tutorial
==========

Structure of Arduino code
--------------------------
Here we will go over the basic structure of the FED3Bandit task. We will use the example in the FED3 arduino library for this explanation.

Sample code
^^^^^^^^^^^
Here is the sample code:

.. code-block:: cpp
  :linenos:

    #include <FED3.h>                             //Include the FED3 library 
    String sketch = "Bandit";                     //Unique identifier text for each sketch, change string only. 
    FED3 fed3 (sketch);                           //Start the FED3 object - don't change

    int pellet_counter = 0;                       //pellet counter variable
    int timeoutIncorrect = 10;                    //timeout duration in seconds, set to 0 to remove the timeout
    int probs[2] = {80,20};                       //Reward probability options
    int new_prob = 0;                

    void setup() {
    fed3.countAllPokes = false;
    fed3.LoRaTransmit = false;
    fed3.pelletsToSwitch = 30;                    // Number of pellets required to finish the block and change reward probabilities
    fed3.prob_left = 80;                          // Initial reward probability of left poke
    fed3.prob_right = 20;                         // Initial reward probability of right poke
    fed3.allowBlockRepeat = false;                // Whether the same probabilities can be used for two blocks in a row
    fed3.begin();                                 // Setup the FED3 hardware, all pinmode screen etc, initialize SD card
    }

    void loop() {
    /////////////////////////////////////////////////////////////////////
    //  This is the main bandit task. 
    //  In general it will be composed of three parts:
    //  1. Set up conditions to trigger a change in reward probabilities
    //  2. Set up behavior upon a left poke
    //  3. Set up behavior upon a right poke
    /////////////////////////////////////////////////////////////////////
        fed3.run();                                   //Call fed.run at least once per loop

        // This is part 1. 
        if (pellet_counter == fed3.pelletsToSwitch) {
            pellet_counter = 0;
            new_prob = probs[random(0,2)];
            if (! fed3.allowBlockRepeat) {
                while (new_prob == fed3.prob_left) {
                    new_prob = probs[random(0,2)];
                }
            }
            fed3.prob_left = new_prob;
            fed3.prob_right = 100 - fed3.prob_left;
        }
        
        // This is part 2. 
        if (fed3.Left) {
            fed3.BlockPelletCount = pellet_counter;
            fed3.logLeftPoke();                                 //Log left poke
            delay(1000);
            if (random(100) < fed3.prob_left) {                      //Select a random number between 0-100 and ask if it is between 0-80 (80% of the time).  If so:
              fed3.ConditionedStimulus();                         //Deliver conditioned stimulus (tone and lights)
              fed3.Feed();                                        //Deliver pellet
            pellet_counter ++;                                  //Increase pellet counter by one
            }
            else {                                              //If random number is between 81-100 (20% of the time)
              fed3.Tone(300, 600);                                //Play the error tone
              fed3.Timeout(timeoutIncorrect, true, true);
            } 
        }

        // This is part 3. 
        if (fed3.Right) {
            fed3.BlockPelletCount = pellet_counter;
            fed3.logRightPoke();                                 //Log Right poke
            delay(1000);
            if (random(100) < fed3.prob_right) {                      //Select a random number between 0-100 and ask if it is between 80-100 (20% of the time).  If so:
              fed3.ConditionedStimulus();                          //Deliver conditioned stimulus (tone and lights)
              fed3.Feed();                                         //Deliver pellet
              pellet_counter ++;                                   //Increase pellet counter by one
            }
            else {                                               //If random number is between 0-80 (80% of the time)
              fed3.Tone(300, 600);                                 //Play the error tone
              fed3.Timeout(timeoutIncorrect, true, true);
            }
        }
    }

This example shows a simple 2-armed bandit task. Here, the reward probabilities of left and right always add 100, and change simultaneously. 
Thus, this is a special case of the 2-armed bandit task that is equivalent to a probabilistic reversal task. This simple version of the bandit
task, however, contains all the fundamental elements for a more sophisticated task. Broadly, FED3Bandit Arduino code is composed of two parts.
First, variable set up. Second, bandit task setup. The task setup part can be further considered in 3 parts: 

1. Reward probability switching
2. Behavior after left poke
3. Behavior after right poke

In the following subsection we will dissect each of the parts of the FED3Bandit bakbone, and in the next section we will show how to customize
each of these parts.

Variable setup
^^^^^^^^^^^^^^^^^^^^^
From the code above, these is where all variables are set up:

.. code-block:: cpp
  :linenos:
    
    #include <FED3.h>                             //Include the FED3 library 
    String sketch = "Bandit";                     //Unique identifier text for each sketch, change string only. 
    FED3 fed3 (sketch);                           //Start the FED3 object - don't change

    int pellet_counter = 0;                       // pellet counter variable
    int timeoutIncorrect = 10;                    // duration in seconds, set to 0 to remove the timeout
    int probs[2] = {80,20};                       // probability options
    int new_prob = 0;                             // 

    void setup() {
    fed3.countAllPokes = false;                   // Whether all pokes are counter 
    fed3.LoRaTransmit = false;                    // Wireless data transmission (future implementation)
    fed3.pelletsToSwitch = 30;                    // Number of pellets required to finish the block and change reward probabilities
    fed3.prob_left = 80;                          // Initial reward probability of left poke
    fed3.prob_right = 20;                         // Initial reward probability of right poke
    fed3.allowBlockRepeat = false;                // Whether the same probabilities can be used for two blocks in a row
    fed3.begin();                                 // Setup the FED3 hardware, all pinmode screen etc, initialize SD card
    }

If you have experience with Arduino programming, this should look very familiar. 

The first block of code includes the FED3 library, and creates a FED3 object with a "Bandit" identifier. If you are using any version
of the bandit task, make sure not to modify the value of ``sketch``, as this initializes ``sessiontype=="Bandit"`` which has unique features
that will not work is ``sketch`` has a different value.

In the second block of code, all variables that are particular to this sketch are declared/initialized. These variables are necessary for
the proper bandit task functioning, but may look different for each version of the task.

Finally, in the third block of code variables that are contained within the FED3 library are initialized. These variables are essential for
any version of FED3Bandit and are doing some work under the hood for all FED3Bandit functions to work properly (specially the logdata() function).
You may modify the value of these variables. For further reference see ARDUINO DOCUMENTATION

Task setup
^^^^^^^^^^^^^
Now that we have discussed the declaration and initialization of all the necessary variables,
let's discuss the task set up. Here's the code of the task:

.. code-block:: cpp
  :linenos:
    
    void loop() {
    /////////////////////////////////////////////////////////////////////
    //  This is the main bandit task. 
    //  In general it will be composed of three parts:
    //  1. Condition(s) to trigger a change in reward probabilities
    //  2. Behavior upon a left poke
    //  3. Behavior upon a right poke
    /////////////////////////////////////////////////////////////////////
        fed3.run();                                   //Call fed.run at least once per loop

        // This is part 1. 
        if (pellet_counter == fed3.pelletsToSwitch) {
            pellet_counter = 0;
            new_prob = probs[random(0,2)];
            if (! fed3.allowBlockRepeat) {
            while (new_prob == fed3.prob_left) {
                new_prob = probs[random(0,2)];
            }
            fed3.prob_left = new_prob;
            fed3.prob_right = 100 - fed3.prob_left;
            }
            else {
            fed3.prob_left = new_prob;
            fed3.prob_right = 100 - fed3.prob_left;
            }
        }
        
        // This is part 2. 
        if (fed3.Left) {
            fed3.BlockPelletCount = pellet_counter;
            fed3.logLeftPoke();                                 //Log left poke
            delay(1000);
            if (random(100) < fed3.prob_left) {                      //Select a random number between 0-100 and ask if it is between 0-80 (80% of the time).  If so:
              fed3.ConditionedStimulus();                         //Deliver conditioned stimulus (tone and lights)
              fed3.Feed();                                        //Deliver pellet
              pellet_counter ++;                                  //Increase pellet counter by one
            }
            else {                                              //If random number is between 81-100 (20% of the time)
              fed3.Tone(300, 600);                                //Play the error tone
              fed3.Timeout(timeoutIncorrect, true, true);
            } 
        }

        // This is part 3. 
        if (fed3.Right) {
            fed3.BlockPelletCount = pellet_counter;
            fed3.logRightPoke();                                 //Log Right poke
            delay(1000);
            if (random(100) < fed3.prob_right) {                      //Select a random number between 0-100 and ask if it is between 80-100 (20% of the time).  If so:
              fed3.ConditionedStimulus();                          //Deliver conditioned stimulus (tone and lights)
              fed3.Feed();                                         //Deliver pellet
              pellet_counter ++;                                   //Increase pellet counter by one
            }
            else {                                               //If random number is between 0-80 (80% of the time)
              fed3.Tone(300, 600);                                 //Play the error tone
              fed3.Timeout(timeoutIncorrect, true, true);
            }
        }
    }

As previously mentioned, the body of the FED3Bandit task consists of three parts:

1. Conditions to trigger a change in reward probabilities:

.. code-block:: cpp
  :linenos:
    
    // This is part 1. 
    if (pellet_counter == fed3.pelletsToSwitch) {
        pellet_counter = 0;
        new_prob = probs[random(0,2)];
        if (! fed3.allowBlockRepeat) {
        while (new_prob == fed3.prob_left) {
            new_prob = probs[random(0,2)];
        }
        fed3.prob_left = new_prob;
        fed3.prob_right = 100 - fed3.prob_left;
        }
        else {
        fed3.prob_left = new_prob;
        fed3.prob_right = 100 - fed3.prob_left;
        }
    }

In this example, reward probabilities change when the mouse have obtained 30 pellets (``fed3.pelletsToSwitch = 30``).

``pellet_counter`` is the variable that tracks the number of pellets that have been received in the current block. 
After 30 pellets have been received, ``pellet_counter`` goes back to zero, a new probability from the reward
probability options ``probs`` is then randomly chosen (in this case there are only two options, 0 or 80). 

Since ``fed3.allowBlockRepeat`` was set to ``false``, a new probability will keep being chosen until ``new_prob`` is
different from ``fed3.prob_left``, and this will be the new value of ``fed3.prob_left``.

In other words, since there are only two possible probabilities, ``fed3.prob_left`` will always be 
``80 -> 20 -> 80 -> ...``. In this case, the new reward probability of right will always be ``100-fed3.prob_left``. 
Leading to the following behavior

========   ================   ==================
Block       fed3.prob_left    fed3.prob_right
========   ================   ==================
1            80                20
2            20                80
3            80                20
========   ================   ==================

And so on. This is behavior is identical to a probabilistic reversal task, showing that this task is a special
case of a two-armed bandit task.

2. Behavior after left poke:

.. code-block:: cpp
  :linenos:
    
    // This is part 2. 
    if (fed3.Left) {
      fed3.BlockPelletCount = pellet_counter;
      fed3.logLeftPoke();                                 //Log left poke
      delay(1000);
      if (random(100) < fed3.prob_left) {                     //Select a random number between 0-100 and ask if it is between 0-80 (80% of the time).  If so:
        fed3.ConditionedStimulus();                         //Deliver conditioned stimulus (tone and lights)
        fed3.Feed();                                        //Deliver pellet
        pellet_counter ++;                                  //Increase pellet counter by one
      }
      else {                                              //If random number is between 81-100 (20% of the time)
        fed3.Tone(300, 600);                                //Play the error tone
        fed3.Timeout(timeoutIncorrect, true, true);
      } 
    }

Here, when the rodent pokes left (``fed3.Left == true``), ``fed3.BlockPelletCount`` is first updated and
the left poke is logged. Then, after a delay of one second (``delay(1000)``), an int between 0 and 100
is selected. 

If the integer is smaller than ``fed3.prob_left``, then a short tone will be played 
(fed3.ConditionedStimulus()) and a pellet will be delivered (``fed3.Feed()``). Due to the inner working
of the feeding funciton, program will stay in this function until the pellet is retrieved.
After the pellet is retrieved, the pellet_counter will be updated.

If the integer is greater than ``fed3.prob_left``, an error tone will be played (``fed3.Tone(300, 600)``) and
a time out of duration ``timeoutIncorrect`` will be triggered. Since the other two argument in the time out
function are ``true, true``, this means that the time out will reset if rodent pokes during time out, and that
pokes that occur during timeout will not be counted on the FED3 screen.

In average, the random integer will be smaller than ``fed3.prob_left`` ``fed3.prob_left`` percent of the times. 
For example if ``fed3.prob_left=80``, a pellet will be delivered 80% of the times, in average.

3. Behavior after right poke

In this example, behavior after a right poke follows the same logic as the behavior after a left poke.

Customizing Task
-------------------

Clearly, a bandit task can be customized in multiple ways. Here we describe a few customization examples.
The goal of this section is to develop intuition of the FED3Bandit structure. Recipes for different
versions of the bandit task can be found in the HOW-TO GUIDES section. All customizations are modifications
of the sample task described above. All modifications of the sample task are highlighted.

Reward probabilities from a normal distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
As we described in the overview section, reward probabilities can be a fixed number or it can come from a 
distribution. Let's say that we want to use the same task as our previous example, but now we want the 
reward probabilities to come from a normal distribution. Let's modify the setup of the variables:

.. code-block:: cpp
  :linenos:
  :emphasize-lines: 2,8,9,22,23,24

    #include <FED3.h>                             //Include the FED3 library 
    #include <random>
    String sketch = "Bandit";                     //Unique identifier text for each sketch, change string only. 
    FED3 fed3 (sketch);                           //Start the FED3 object - don't change

    int pellet_counter = 0;                       // pellet counter variable
    int timeoutIncorrect = 10;                    // duration in seconds, set to 0 to remove the timeout
    int probs_mean[2] = {80,20};                  // probability options
    int probs_std = 10:
    int new_prob = 0;                             // 

    void setup() {
    fed3.countAllPokes = false;                   // Whether all pokes are counter 
    fed3.LoRaTransmit = false;                    // Wireless data transmission (future implementation)
    fed3.pelletsToSwitch = 30;                    // Number of pellets required to finish the block and change reward probabilities
    fed3.prob_left = 80;                          // Initial reward probability of left poke
    fed3.prob_right = 20;                         // Initial reward probability of right poke
    fed3.allowBlockRepeat = false;                // Whether the same probabilities can be used for two blocks in a row
    fed3.begin();                                 // Setup the FED3 hardware, all pinmode screen etc, initialize SD card
    }

    std::default_random_engine generator;
    std::normal_distribution<float> distribution_left(fed3.prob_left, probs_std);
    std::normal_distribution<float> distribution_right(fed3.prob_lright, probs_std);

First, notice that we included the ``<random>`` library.
We have also changed ``int probs[2] = {80,20}`` to ``int probs_mean[2] = {80,20}`` to reflect that these will not
be fixed but the mean of the normal distribution. Similarly, we added a new variable ``int probs_std = 10`` that
will be the standard deviation of the normal distribution. Finally, we create a random_engine 
instance (``generator``), which will help us select a random number from the normal distribution, and two normal
distributions (``distribution_left`` and ``distribution_right``).

Since we want to change the mean of the distribution after the block switchin condition has been met (in this
case after 30 pellets have been delivered) we modify the condition section as follows:

.. code-block:: cpp
  :linenos:
  :emphasize-lines: 11,12,17,18

    // This is part 1. 
    if (pellet_counter == fed3.pelletsToSwitch) {
        pellet_counter = 0;
        new_prob = probs[random(0,2)];
        if (! fed3.allowBlockRepeat) {
          while (new_prob == fed3.prob_left) {
            new_prob = probs[random(0,2)];
          }
        fed3.prob_left = new_prob;
        fed3.prob_right = 100 - fed3.prob_left;
        std::normal_distribution<float> distribution_left(fed3.prob_left, probs_std);
        std::normal_distribution<float> distribution_right(fed3.prob_lright, probs_std);
        }
        else {
          fed3.prob_left = new_prob;
          fed3.prob_right = 100 - fed3.prob_left;
          std::normal_distribution<float> distribution_left(fed3.prob_left, probs_std);
          std::normal_distribution<float> distribution_right(fed3.prob_lright, probs_std);
        }
    }

Here instead of just changing the value of ``probs_left`` and ``probs_right``, we are creating two new normal
distributions that have the new mean (``distribution_left``, ``distribution_right``).

Now, let's see how we need to adapt the behavior after a left poke (and right poke identically) to deliver
a pellet with a probability drawn from a normal distribution:

.. code-block:: cpp
  :linenos:
  :emphasize-lines: 6

    // This is part 2. 
    if (fed3.Left) {
      fed3.BlockPelletCount = pellet_counter;
      fed3.logLeftPoke();                                 //Log left poke
      delay(1000);
      float normal_left = distribution_left(generator);
      if (random(100) < normal_left) {                     //Select a random number between 0-100 and ask if it is between 0-80 (80% of the time).  If so:
        fed3.ConditionedStimulus();                         //Deliver conditioned stimulus (tone and lights)
        fed3.Feed();                                        //Deliver pellet
        pellet_counter ++;                                  //Increase pellet counter by one
      }
      else {                                              //If random number is between 81-100 (20% of the time)
        fed3.Tone(300, 600);                                //Play the error tone
        fed3.Timeout(timeoutIncorrect, true, true);
      } 
    }

Here after a left poke, but before evaluating the outcome, we draw a number from ``distribution_left`` 
(``normal_left``) and evaluate the outcome based on that number. A similar modification would be needed
to the FED3 behavior after a right poke.

Independence of arms
^^^^^^^^^^^^^^^^^^^^^
Up until now, the two "arms" of the bandit task have been dependent on each other. The sum of ``prob_left``
and ``prob_right`` has always been equal to 100. However, this does not need to be the case. Let's say that
in this version of the task we want more than two probability options and we want the probabilities to
be chosen independently for each arm. To do this we adapt the variable setup as follows:
    
.. code-block:: cpp
  :linenos:
  :emphasize-lines: 7,9,10,16,17
    
    #include <FED3.h>                             //Include the FED3 library 
    String sketch = "Bandit";                     //Unique identifier text for each sketch, change string only. 
    FED3 fed3 (sketch);                           //Start the FED3 object - don't change

    int pellet_counter = 0;                       // pellet counter variable
    int timeoutIncorrect = 10;                    // duration in seconds, set to 0 to remove the timeout
    int probs[5] = {90,70,50,30,10};              // probability options
    int probs_std = 10:
    int new_prob_left = 0;                             // 
    int new_prob_right = 0;

    void setup() {
    fed3.countAllPokes = false;                   // Whether all pokes are counter 
    fed3.LoRaTransmit = false;                    // Wireless data transmission (future implementation)
    fed3.pelletsToSwitch = 30;                    // Number of pellets required to finish the block and change reward probabilities
    fed3.prob_left = 90;                          // Initial reward probability of left poke
    fed3.prob_right = 90;                         // Initial reward probability of right poke
    fed3.allowBlockRepeat = false;                // Whether the same probabilities can be used for two blocks in a row
    fed3.begin();                                 // Setup the FED3 hardware, all pinmode screen etc, initialize SD card
    }

Here, we have modified ``probs`` to contain 5 values: 90, 70, 50, 30, 10. This provides more options of reward
probabilities. We have also change the name of ``new_prob`` to ``new_prob_left`` and initialized a new variable 
called ``new_prob_right`` Note that we also changed the initial value of ``fed3.prob_left`` and ``fed3.prob_right`` 
to be one of the options from ``probs``. Also note that the sum of the two does not equal to 100. 

Now, we need to change what happens when the condition for switching probabilities is met:

.. code-block:: cpp
  :linenos:
  :emphasize-lines: 4,5,7,8,10,11,13,14,17,18

    // This is part 1. 
    if (pellet_counter == fed3.pelletsToSwitch) {
        pellet_counter = 0;
        new_prob_left = probs[random(0,5)];
        new_prob_right = probs[random(0,5)];
        if (! fed3.allowBlockRepeat) {
          while (new_prob_left == fed3.prob_left) {
            new_prob_left = probs[random(0,2)];
          }
          while (new_prob_right == fed3.prob_right) {
            new_prob_right = probs[random(0,2)];
          }
        fed3.prob_left = new_prob_left;
        fed3.prob_right = new_prob_right;
        }
        else {
          fed3.prob_left = new_prob_left;
          fed3.prob_right = nw_prob_right;
        }
    }

Here we are repeating the procedure of choosing a probability from ``probs`` for ``new_prob_left``
and ``new_prob_right``. Since ``random()`` is called twice, two different values will likely be assigned
to each.

Creating conditions for reward probability changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Up until now, the condition for switching reward probabilities has been to reach 30 pellets delivered.
Let's say that we want to change this condition. The new condition will be that the rodent needs to poke
seven times on the high probability port, and after that the reward probabilities will change. Let's modify
the variable setup first:

.. code-block:: cpp
  :linenos:
  :emphasize-lines: 9,14

    #include <FED3.h>                             //Include the FED3 library 
    String sketch = "Bandit";                     //Unique identifier text for each sketch, change string only. 
    FED3 fed3 (sketch);                           //Start the FED3 object - don't change

    int pellet_counter = 0;                       // pellet counter variable
    int timeoutIncorrect = 10;                    // duration in seconds, set to 0 to remove the timeout
    int probs[2] = {80,20};                       // probability options
    int new_prob = 0;                             // 
    int high_p_pokes = 0;

    void setup() {
    fed3.countAllPokes = false;                   // Whether all pokes are counter 
    fed3.LoRaTransmit = false;                    // Wireless data transmission (future implementation)
    fed3.pelletsToSwitch = 7;                    // Number of pellets required to finish the block and change reward probabilities
    fed3.prob_left = 80;                          // Initial reward probability of left poke
    fed3.prob_right = 20;                         // Initial reward probability of right poke
    fed3.allowBlockRepeat = false;                // Whether the same probabilities can be used for two blocks in a row
    fed3.begin();                                 // Setup the FED3 hardware, all pinmode screen etc, initialize SD card
    }

Here, we initialized a new variable called ``high_p_pokes`` which will be the counter of high probability pokes.
We also changed the value of ``fed3.pelletsToSwitch`` to 7. Note that the new condition will not require any
specific number of pellets, but ``fed3.pelletsToSwitch`` is printed in the .csv output file. Alternatively,
we could also set ``fed3.pelletsToSwitch = 0`` and initialize a new variable ``int high_p_cond = 7`` and replace
all ``fed3.pelletsToSwitch`` in the rest of the code. However, using this alternative the condition will not be
printed in the csv file. Now let's take a look at part 1 of the task setup:

.. code-block:: cpp
  :linenos:
  :emphasize-lines: 2,3

    // This is part 1. 
    if (high_p_pokes == fed3.pelletsToSwitch) {
      high_p_pokes = 0;
      new_prob = probs[random(0,2)];
      if (! fed3.allowBlockRepeat) {
          while (new_prob == fed3.prob_left) {
              new_prob = probs[random(0,2)];
          }
      }
      fed3.prob_left = new_prob;
      fed3.prob_right = 100 - fed3.prob_left;
    }

The only change we made here was to replace ``pellet_counter`` with ``high_p_pokes``. Finally, we need to 
when ``high_p_pokes`` will increase. Let's see how this looks after a left poke

.. code-block:: cpp
  :linenos:
  :emphasize-lines: 6,7,8,9,10,11

    // This is part 2. 
    if (fed3.Left) {
      fed3.BlockPelletCount = pellet_counter;
      fed3.logLeftPoke();                                 //Log left poke
      delay(1000);
      if (prob_left > 50) {
        high_p_pokes ++;
      }
      else {
        high_p_pokes = 0;
      }

      if (random(100) < normal_left) {                     //Select a random number between 0-100 and ask if it is between 0-80 (80% of the time).  If so:
        fed3.ConditionedStimulus();                         //Deliver conditioned stimulus (tone and lights)
        fed3.Feed();                                        //Deliver pellet
        pellet_counter ++;                                  //Increase pellet counter by one
      }
      else {                                              //If random number is between 81-100 (20% of the time)
        fed3.Tone(300, 600);                                //Play the error tone
        fed3.Timeout(timeoutIncorrect, true, true);
      } 
    }

Here we have added a new conditional statement. If the left port is the high probability port (``prob_left > 50``)
then ``high_p_pokes`` will increase by one. Otherwise, it will be reset to 0. If we add the same conditional
statement after a right poke (replacing ``prob_left > 50`` with ``prob_right > 50``), ``high_p_pokes`` will only
reach 7 (number needed to trigger a reward probability change) after the rodent pokes 7 consecutive times in the
higher probability port.

Other Customizations
^^^^^^^^^^^^^^^^^^^^^
The objective of this tutorial is to develop intuition on how the FED3Bandit task is setup. For additional
versions of FED3Bandit, please see the HOW-TO GUIDE section.


