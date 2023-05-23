from PFSTA import PFSTA
import over_under
from expectation_maximization import (  likelihood_no_order,
                                        likelihood_no_order_sst,
                                        update_no_order_until,
                                        update_n,
                                        update_no_order_until_pen,
                                        update_no_order_until_sst)
import tree_generator
import time
from mle import pfsta_mle
from parsing import split_bank
from collections import Counter

assignment = {0: 'L', 1: 'N', 2: 'V', 3: 'NP', 4: 'UL'}

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

goal_pfsta_2 = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'WH', ()): 1.0,
                         (1, '*', (0, 4)): 0.297,
                         (1, '*', (1, 1)): 0.2339,
                         (1, '*', (2, 3)): 0.2612,
                         (1, 'X', ()): 0.2079,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (2,)): 0.5122,    # unary branching for unlicensed V
                         (4, '*', (1, 4)): 0.4878})

goal_pfsta_3 = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'WH', ()): 1.0,
                         (1, '*', (0, 4)): 0.047,
                         (1, '*', (1, 1)): 0.4339,
                         (1, '*', (2, 3)): 0.0112,
                         (1, 'X', ()): 0.5079,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (2,)): 0.5122,    # unary branching for unlicensed V
                         (4, '*', (1, 4)): 0.4878})

goal_pfsta_4 = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'WH', ()): 1.0,
                         (1, '*', (0, 4)): 0.027,
                         (1, '*', (1, 1)): 0.3039,
                         (1, '*', (2, 3)): 0.0512,
                         (1, 'X', ()): 0.6179,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (2,)): 0.5122,    # unary branching for unlicensed V
                         (4, '*', (1, 4)): 0.4878})


goal_pfsta_5 = PFSTA(  [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'WH', ()): 1.0,
                         (1, '*', (0, 4)): 0.017,
                         (1, '*', (1, 1)): 0.4479,
                         (1, '*', (2, 3)): 0.0332,
                         (1, 'X', ()): 0.4569,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (2,)): 0.5001,    # unary branching for unlicensed V
                         (4, '*', (1, 4)): 0.4999})

CHILDES_mle_pfsta = PFSTA([0, 1, 2, 3, 4],
                          {1: 1.0},
                          {(0, 'WH', ()): 1.0,
                          (1, '*', (0, 4)): 0.0224,
                          (1, '*', (1, 1)): 0.3994,
                          (1, '*', (2, 3)): 0.1534,
                          (1, 'X', ()): 0.4249,
                          (2, 'V', ()): 1.0,
                          (3, 'NP', ()): 1.0,
                          (4, '*', (2,)): 0.3684,
                          (4, '*', (1, 4)): 0.6316 })

num_trees = int(input("How many trees would you like to generate?  "))
enforce_depth = input("Would you like to enforce a maximum depth? (y/n) ")
enforce_depth = True if enforce_depth == 'y' else False
max_depth = None
if enforce_depth:
    max_depth = int(input("\tMax depth: "))
verbose = input("Would you like print the trees? (y/n) ")
verbose = True if verbose == 'y' else False

print('PFSTA used to generate:')
CHILDES_mle_pfsta.clean_print()

print("\nGenerating", num_trees, "trees...\n")
bank = tree_generator.generate_bank_from_pfsta(CHILDES_mle_pfsta, num_trees, max_depth)

print('--Treebank--')
if verbose:
    for t in bank:
        over_under.print_tree(t)
        print('---')

print('Distribution:')
resplit_bank = split_bank(bank)
for k, v in resplit_bank.items():
    print('\t', k+': %.2f' % (len(v)/len(bank)))

wh_count = 0
np_count = 0
c_only_count = 0
for t in bank:
    terminals = Counter(over_under.get_terminals(t))
    wh_count += terminals['WH']
    np_count += terminals['NP']
    if 'NP' not in terminals.keys() and 'WH' not in terminals.keys():
        c_only_count += 1
print ({'WH transitions': wh_count, 'NP transitions': np_count, 'C only': c_only_count})


d = 0
for t in bank:
    d += len(over_under.depth(t))
print('Avg depth:', d/len(bank))

mle = pfsta_mle(bank)
print('MLE PFSTA:')
mle.clean_print()

print('---')
print('Learning...')
num_pfstas = 10
new_pfstas = []
highest = -2000000000
index = 0
random_initialization_times = []
update_n_times = []
likelihood_times = []
for i in range(num_pfstas):
    print('Initialization #', i+1)
    p = PFSTA()
    over_under.initialize_random(p, 4, ['WH', 'V', 'X', 'NP'])
    # p.print()
    # print('--')
    st = time.time()
    # new_p = update_no_order_until(p, bank, 0.1) # REG
    # new_p = update_no_order_until_sst(p, bank, 0.1) # SST
    new_p, new_p_likelihood = update_no_order_until_pen(p, bank, 0.1) # PEN

    
    et = time.time()
    update_n_times.append(et-st)
    # new_p_likelihood = likelihood_no_order(new_p, bank) # REG
    # new_p_likelihood = likelihood_no_order_sst(new_p, bank) # SST

    if new_p_likelihood > highest:
        index = i
        highest = new_p_likelihood
    new_pfstas.append(new_p)
    new_p.pretty_print(assignment)
    print('------')

best = new_pfstas[index]

print("Best likelihood (from ",num_pfstas, " initializations):")
# print(likelihood_no_order(best, bank)) # REG
# print(likelihood_no_order_sst(best, bank)) # SST
# print(likelihood_counts(best, bank)) # PEN


best.clean_print()
print("CFG form:")
best.pretty_print(assignment)

# mle_likelihood = likelihood_no_order(mle, bank)
# print('Likelihood with MLE PFSTA:', mle_likelihood, '\n')

# print("\nUpdate until .01 avg time:", sum(update_n_times)/len(update_n_times)/60, "mins")
