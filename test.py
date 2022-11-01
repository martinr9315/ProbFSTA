from PFSTA import PFSTA, Node
import over_under
from expectation_maximization import (ObservedEvents,
                                      likelihood, likelihood_no_order, update, update_n,
                                      update_no_order, update_no_order_n,
                                      expectations_from_corpus_no_order,
                                      expectations_from_corpus, update_no_order_until)
import tree_generator
import time

# bank = tree_generator.generate_bank(['Wh', 'V', 'C', 'NP'], 4, 100)
# for t in bank:
#     over_under.print_tree(t)
#     print("--")

assignment = {0: 'L', 1: 'N', 2: 'V', 3: 'NP', 4: 'UL'}

trees = tree_generator.read_from_file("more_trees.txt")

new_pfstas = []
highest = -20000000
index = 0
random_initialization_times = []
update_n_times = []
likelihood_times = []
for i in range(5):
    p = PFSTA()
    over_under.initialize_random(p, 4, ['Wh', 'V', 'C', 'NP'])
    print(i)
    p.clean_print()
    print('--')
    st = time.time()
    new_p = update_no_order_until(p, trees, 1)
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

# best = highest_likelihood(new_pfstas, trees)
best = new_pfstas[index]
print("Best:", likelihood_no_order(best, trees))
best.clean_print()
best.pretty_print(assignment)
# print(highest)

print("update until 1 avg time:", sum(update_n_times)/len(update_n_times)/60, "mins")
