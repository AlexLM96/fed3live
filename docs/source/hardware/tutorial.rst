Tutorial
==========

Structure of Arduino code
--------------------------
Here we will go over the basic structure of the FED3Bandit task. We will use the example in the FED3 arduino library for this explanation.

Sample code
^^^^^^^^^^^
Here is the sample code::

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
            while (new_prob == prob_left) {
                new_prob = probs[random(0,2)];
            }
            prob_left = new_prob;
            prob_right = 100 - prob_left;
            }
            else {
            prob_left = new_prob;
            prob_right = 100 - prob_left;
            }
        }
        
        // This is part 2. 
        if (fed3.Left) {
            fed3.BlockPelletCount = pellet_counter;
            fed3.logLeftPoke();                                 //Log left poke
            delay(1000);
            if (random(100) < prob_left) {                      //Select a random number between 0-100 and ask if it is between 0-80 (80% of the time).  If so:
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
            if (random(100) < prob_right) {                      //Select a random number between 0-100 and ask if it is between 80-100 (20% of the time).  If so:
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
From the code above, these is where all variables are set up::
    
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
let's discuss the task set up. Here's the code of the task::
    
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
            while (new_prob == prob_left) {
                new_prob = probs[random(0,2)];
            }
            prob_left = new_prob;
            prob_right = 100 - prob_left;
            }
            else {
            prob_left = new_prob;
            prob_right = 100 - prob_left;
            }
        }
        
        // This is part 2. 
        if (fed3.Left) {
            fed3.BlockPelletCount = pellet_counter;
            fed3.logLeftPoke();                                 //Log left poke
            delay(1000);
            if (random(100) < prob_left) {                      //Select a random number between 0-100 and ask if it is between 0-80 (80% of the time).  If so:
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
            if (random(100) < prob_right) {                      //Select a random number between 0-100 and ask if it is between 80-100 (20% of the time).  If so:
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

1. Conditions to trigger a change in reward probabilities::
    
    // This is part 1. 
    if (pellet_counter == fed3.pelletsToSwitch) {
        pellet_counter = 0;
        new_prob = probs[random(0,2)];
        if (! fed3.allowBlockRepeat) {
        while (new_prob == prob_left) {
            new_prob = probs[random(0,2)];
        }
        prob_left = new_prob;
        prob_right = 100 - prob_left;
        }
        else {
        prob_left = new_prob;
        prob_right = 100 - prob_left;
        }
    }

In this example, reward probabilities change when the mouse have obtained 30 pellets (``fed3.pelletsToSwitch = 30``).

``pellet counter`` is the variable that tracks the number of pellets that have been received in the current block. 
After 30 pellets have been received, ``pellet counter`` goes back to zero, a new probability from the reward
probability options ``probs`` is then randomly chosen (in this case there are only two options, 0 or 80). 

Since ``fed3.allowBlockRepeat`` was set to ``false``, a new probability will keep being chosen until ``new_prob`` is
different from ``prob_left``, and this will be the new value of ``prob_left``.

In other words, since there are only two possible probabilities, ``prob_left`` will always be 
``80 -> 20 -> 80 -> ...``. In this case, the new reward probability of right will alwas be ``100-prob_left``. 
Leading to the following behavior

========   ===========   ===========
Block       prob_left    prob_right
========   ===========   ===========
1            80            20
2            20            80
3            80            20
========   ===========   ===========

And so on. This is behavior is identical to a probabilistic reversal task, showing that this task is a special
case of a two-armed bandit task.


Customizing Task
-------------------------------------

Reward probabilities
^^^^^^^^^^^^^^^^^^^^^

Independence of arms
^^^^^^^^^^^^^^^^^^^^^

Creating conditions for reward probability changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Time out options
^^^^^^^^^^^^^^^^^







