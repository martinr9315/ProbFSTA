from PFSTA import PFSTA
import over_under
from expectation_maximization import (  likelihood_no_order,
                                        update_no_order_until,
                                        update_n)
from parsing import parse, timeout_handler
import time, signal, random


NUM_PFSTAS = 25     # number of randomly initialized PFSTAs
NUM_TREES = 50      # number of trees to randomly sample from CHILDES
TIME_LIMIT = 300    # set the time limit in seconds


assignment = {0: 'L', 1: 'N', 2: 'V', 3: 'NP', 4: 'UL'}


bank = parse(20000)
bank = random.sample(bank, NUM_TREES)

for t in bank:
    over_under.print_tree(t)
    print('--')


new_pfstas = []
highest = -2000000000
index = 0
update_n_times = []
timeouts = 0
for i in range(NUM_PFSTAS):
    print('#', i+1)
    p = PFSTA()
    over_under.initialize_random(p, 4, ['WH', 'V', 'C', 'NP'])
    p.clean_print()
    print('--')
    st = time.time()

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(TIME_LIMIT)
    try:
        new_p = update_no_order_until(p, bank, 0.1)
    except TimeoutError as e:
        print(e)
        timeouts += 1
        continue
    else:
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
    finally:
        signal.alarm(0)


best = new_pfstas[index]
print("Best likelihood (from ", num_pfstas, "initializations, ", num_trees, "trees):", likelihood_no_order(best, bank))
best.clean_print()
print("CFG form:")
best.pretty_print(assignment)
print("\nTimed out on ", timeouts)
# print("\nUpdate until .01 avg time:", sum(update_n_times)/len(update_n_times)/60, "mins")


