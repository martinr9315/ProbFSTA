# prob-fsta

## *Ling 198B: Modelling Learning of Long Distance Dependencies Using PFSTA Expectation Maximization*

Presented at UCLA Undergraduate Research Week. 
Slides can be found [here](CL_slides.pptx) and paper can be found [here](Long_Distance_Wh-Dependency.pdf). Authored by Roxane Martin, supervised by Tim Hunter and Yang Wang.


#### CHILDES Trials

##### Parsing
The parsing of the CHILDES database occurs in trees.py and parsing.py. The parses in the database are cleaned to only contain transitive verbs and wh-licensing of transitive verbs, leaving the rest as neutral 'X' terminals.

##### Learning
To run the EM learner on trees from the CHILDES database, run ```python learn.py```. The global variables NUM_PFSTAS, NUM_TREES, TIME_LIMIT, set the number of randomly initialized PFSTAs, the number of trees to randomly sample from CHILDES, and the computation time limit in seconds, respectively.

##### Regularization
There are implementation of multiple types of regularization within  ```expectation_maximization.py```. Currently, ```learn.py``` and ```run_trials.py``` both use a statewise entropy penalty with a factor of 25 as a regularizer. The regularization factor can be adjusted by adjusting the global variable ```LAMBDA``` and the type of regularizer can be adjusted by following the two ```TODO``` comments, both in ```expectation_maximization.py```.


##### Random Starting PFSTA
The EM algorithm requires a random PFSTA from which to begin iteration. Currently, the random starting PFSTA (and subsequent EM algorithm) default to being **unorded**, having **assigned terminal states** (i.e., the 0 state always corresponds to the 'WH' terminal), and an **assigned initial state** (equivalent to a resolved dependency since state 1, the neutral state, is the assigned initial state). 

As of now, these are modifiable via the global variables in ```over_under.py```.

#### Learner Development
Before testing the learner on the CHILDES database, it was tested by running trials on example treebanks both built by hand and generated from PFSTAs, as explained below.


##### Running Trials
To run a trial, run: ```python3 run_trials.py``` and follow the prompts. This uses the treebank generation described below to produce a treebnak for learning.  The various randomly initialized PFSTAs are displayed, and then learned PFSTA and corresponding CFG that produces the best likelihood from 50 random initializations.

##### Tree Bank Generation
A tree bank can be generated from a  Probalistic Finite State Tree Automata, the PFSTA which we want the learner to learn.
Currently, the generating PFSTA is the MLE PFSTA calculated from annotating the CHILDES treebank: 
```
    Q: [0, 1, 2, 3, 4]
    I: {0: 0.0, 1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0}
    Delta:
    (0, 'WH', ()): 1.0,
    (1, '*', (0, 4)): 0.0224,
    (1, '*', (1, 1)): 0.3994,
    (1, '*', (2, 3)): 0.1534,
    (1, 'X', ()): 0.4249,
    (2, 'V', ()): 1.0,
    (3, 'NP', ()): 1.0,
    (4, '*', (2,)): 0.3684,
    (4, '*', (1, 4)): 0.6316                                 
```
To exclusively generate a tree bank, run: ```python3 generate_trees.py``` (this is not necessary if running trials, as the treebank is automatically generated) and follow the prompts to specify number of trees and output location. 


