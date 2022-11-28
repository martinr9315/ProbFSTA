from PFSTA import PFSTA
import over_under
from expectation_maximization import (  likelihood_no_order,
                                        update_no_order_until,
                                        update_n)
import tree_generator
import time

assignment = {0: 'L', 1: 'N', 2: 'V', 3: 'NP', 4: 'UL'}

goal_pfsta = PFSTA( [0, 1, 2, 3, 4],
                    {1: 1.0},
                    {(0, 'Wh', ()): 1.0,
                    (1, '*', (0, 4)): 0.0688,
                    (1, '*', (1, 1)): 0.2982,
                    (1, '*', (2, 3)): 0.2523,
                    (1, 'C', ()): 0.3807,
                    (2, 'V', ()): 1.0,
                    (3, 'NP', ()): 1.0,
                    (4, '*', (1, 2)): 0.6818,
                    (4, '*', (1, 4)): 0.3182})

bank = tree_generator.read_from_file("treebanks/50_free_depth.txt")


new_pfstas = []
highest = -20000000
index = 0
random_initialization_times = []
update_n_times = []
likelihood_times = []
for i in range(15):
    print('#', i+1)
    p = PFSTA()
    over_under.initialize_random(p, 4, ['Wh', 'V', 'C', 'NP'])
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
print("Best:", likelihood_no_order(best, bank))
best.clean_print()
best.pretty_print(assignment)

print("update until .01 avg time:", sum(update_n_times)/len(update_n_times)/60, "mins")
