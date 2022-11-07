from PFSTA import PFSTA
import over_under
from expectation_maximization import (likelihood_no_order,
                                      update_no_order_until)
import tree_generator
import time

assignment = {0: 'L', 1: 'N', 2: 'V', 3: 'NP', 4: 'UL'}

trees = tree_generator.read_from_file("treebanks/generated_bank_25.txt")

new_pfstas = []
highest = -20000000
index = 0
random_initialization_times = []
update_n_times = []
likelihood_times = []
for i in range(5):
    print('#', i+1)
    p = PFSTA()
    over_under.initialize_random(p, 4, ['Wh', 'V', 'C', 'NP'])
    p.clean_print()
    print('--')
    st = time.time()
    new_p = update_no_order_until(p, trees, .1)
    et = time.time()
    update_n_times.append(et-st)
    new_p_likelihood = likelihood_no_order(new_p, trees)
    if new_p_likelihood > highest:
        index = i
        highest = new_p_likelihood
    new_pfstas.append(new_p)
    print(likelihood_no_order(p, trees), '-->', new_p_likelihood)
    new_p.pretty_print(assignment)
    print('------')

best = new_pfstas[index]
print("Best:", likelihood_no_order(best, trees))
best.clean_print()
best.pretty_print(assignment)

print("update until .1 avg time:", sum(update_n_times)/len(update_n_times)/60, "mins")
