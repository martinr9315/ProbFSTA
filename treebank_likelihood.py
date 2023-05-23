from PFSTA import PFSTA
import over_under
from expectation_maximization import (  likelihood_no_order,
                                        update_no_order_until,
                                        update_n)
from parsing import parse, split_bank, depth_limit, timeout_handler
import time, signal, random, copy


goal_pfsta = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'WH', ()): 1.0,
                         (1, '*', (0, 4)): 0.097,
                         (1, '*', (1, 1)): 0.2239,
                         (1, '*', (2, 3)): 0.2612,
                         (1, 'X', ()): 0.4179,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (2,)): 0.7222,    # unary branching for unlicensed V
                         (4, '*', (1, 4)): 0.2778})


NUM_PFSTAS = 25             # number of randomly initialized PFSTAs
NUM_TREES = 50              # number of trees to randomly sample from CHILDES
TIME_LIMIT = 900            # set the time limit in seconds
MAX_DEPTH = 5

assignment = {0: 'L', 1: 'N', 2: 'V', 3: 'NP', 4: 'UL'}


bank = parse(20000)
split_bank = split_bank(bank)

bank = random.sample(bank, 100)

wh_bank = random.sample(depth_limit(split_bank['wh_only'], MAX_DEPTH), NUM_TREES)
v_np_bank = random.sample(depth_limit(split_bank['v_np_only'], MAX_DEPTH), NUM_TREES)
c_bank = random.sample(depth_limit(split_bank['c_only'], MAX_DEPTH), NUM_TREES)

bank = wh_bank+v_np_bank+c_bank

likelihood = likelihood_no_order(goal_pfsta, bank)
