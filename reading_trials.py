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
                    {(0, 'WH', ()): 1.0,
                    (1, '*', (0, 4)): 0.0688,
                    (1, '*', (1, 1)): 0.2982,
                    (1, '*', (2, 3)): 0.2523,
                    (1, 'X', ()): 0.3807,
                    (2, 'V', ()): 1.0,
                    (3, 'NP', ()): 1.0,
                    (4, '*', (1, 2)): 0.6818,
                    (4, '*', (1, 4)): 0.3182})


input_file = input("Which treebank would you like to use? ")
if '.txt' in input_file:
    input_file = input("Input filename w/o ext: ")
bank = tree_generator.read_from_file("treebanks/"+input_file+".txt")

num_pfstas = 50
new_pfstas = []
highest = -2000000000
index = 0
random_initialization_times = []
update_n_times = []
likelihood_times = []
for i in range(num_pfstas):
    print('#', i+1)
    p = PFSTA()
    over_under.initialize_random(p, 4, ['WH', 'V', 'X', 'NP'])
    p.clean_print()
    print('--')
    st = time.time()
    new_p = update_no_order_until(p, bank, 0.1)
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
print("\nUsing bank "+input_file+"...")
print(""+input_file)
print("Best likelihood (from "+num_pfstas+" initializations):", likelihood_no_order(best, bank))
best.clean_print()
print("CFG form:")
best.pretty_print(assignment)

# print("\nUpdate until .01 avg time:", sum(update_n_times)/len(update_n_times)/60, "mins")
