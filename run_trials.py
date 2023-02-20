from PFSTA import PFSTA
import over_under
from expectation_maximization import (  likelihood_no_order,
                                        update_no_order_until,
                                        update_n)
import tree_generator
import time

assignment = {0: 'L', 1: 'N', 2: 'V', 3: 'NP', 4: 'UL'}

goal_pfsta_3 = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'WH', ()): 1.0,
                         (1, '*', (0, 4)): 0.097,
                         (1, '*', (1, 1)): 0.2239,
                         (1, '*', (2, 3)): 0.2612,
                         (1, 'C', ()): 0.4179,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (2,)): 0.7222,    # unary branching for unlicensed V
                         (4, '*', (1, 4)): 0.2778})

num_trees = int(input("How many trees would you like to generate?  "))
enforce_depth = input("Would you like to enforce a maximum depth? (y/n) ")
enforce_depth = True if enforce_depth == 'y' else False
max_depth = None
if enforce_depth:
    max_depth = int(input("\tMax depth: "))
verbose = input("Would you like print the trees? (y/n) ")

print("\nGenerating", num_trees, "trees...\n")
bank = tree_generator.generate_bank_from_pfsta(goal_pfsta_3, num_trees, max_depth)
print('--Treebank--')
if verbose:
    for t in bank:
        over_under.print_tree(t)
        print('---')

print('Learning...')
num_pfstas = 25
new_pfstas = []
highest = -2000000000
index = 0
random_initialization_times = []
update_n_times = []
likelihood_times = []
for i in range(num_pfstas):
    print('Initialization #', i+1)
    p = PFSTA()
    over_under.initialize_random(p, 4, ['WH', 'V', 'C', 'NP'])
    p.clean_print()
    print('--')
    st = time.time()
    new_p = update_no_order_until(p, bank, 0.01)
    et = time.time()
    update_n_times.append(et-st)
    new_p_likelihood = likelihood_no_order(new_p, bank)
    if new_p_likelihood > highest:
        index = i
        highest = new_p_likelihood
    new_pfstas.append(new_p)
    print(likelihood_no_order(p, bank), '-->', new_p_likelihood)
    new_p.pretty_print(assignment)
    print('------')

best = new_pfstas[index]
print("Best likelihood (from ",num_pfstas, " initializations):", likelihood_no_order(best, bank))
best.clean_print()
print("CFG form:")
best.pretty_print(assignment)

# print("\nUpdate until .01 avg time:", sum(update_n_times)/len(update_n_times)/60, "mins")
