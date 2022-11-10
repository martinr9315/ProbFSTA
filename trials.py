from PFSTA import PFSTA
import over_under
import expectation_maximization 
#import (likelihood_no_order,
#                                       update_no_order_until, tree_prob_via_under_no_order,
#                                       tree_prob_via_over_no_order)
import tree_generator
import time


# tree w/ depth>4 read correctly (try only right branching)
# if yes, then check over_no_order prob and under_no_order prob



assignment = {0: 'L', 1: 'N', 2: 'V', 3: 'NP', 4: 'UL'}

trees = tree_generator.read_from_file("treebanks/V_Wh_trees.txt")



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

for t in trees:
    print("under", over_under.tree_prob_via_under_no_order(goal_pfsta, t))
    print("over", over_under.tree_prob_via_over_no_order(goal_pfsta, t))

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
