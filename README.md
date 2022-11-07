### Ling 198A: Modelling Learning of Long Distance Dependencies Using Expectation Maximization

#### Tree Bank Generation

A tree bank can be generated from a 'goal PFSTA,' the PFSTA which we want the learner to learn.
Currently, the goal PFSTA is set to be: 
```
    Q: [0, 1, 2, 3, 4]
    I: {0: 0.0, 1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0}
    Delta:
    (0, 'Wh', ()):1.0
    (1, '*', (0, 4)):0.0688
    (1, '*', (1, 1)):0.2982
    (1, '*', (2, 3)):0.2523
    (1, 'C', ()):0.3807
    (2, 'V', ()):1.0
    (3, 'NP', ()):1.0
    (4, '*', (1, 2)):0.6818
    (4, '*', (1, 4)):0.3182
```
To generate a tree bank, run: ```python3 generate_trees.py``` and follow the prompts to specify number of trees and output location. 

#### Random Starting PFSTA
The EM algorithm requires a random PFSTA from which to begin iteration. Currently, the random starting PFSTA (and subsequent EM algorithm) default to being **unorded**, having **assigned terminal states** (i.e., the 0 state always corresponds to the 'Wh' terminal), and an **assigned initial state** (equivalent to a resolved dependency since state 1, the neutral state, is the assigned initial state). 

As of now, these are modifiable via the global variables in ```over_under.py```.