from expectation_maximization import    (update_no_order_until, 
                                        likelihood_no_order, 
                                        update_no_order_until_pen,
                                        update_pen)
from PFSTA import PFSTA
import over_under
import tree_generator
import time
from parsing import split_bank
from collections import Counter
import numpy as np


assignment = {0: 'L', 1: 'N', 2: 'V', 3: 'NP', 4: 'UL'}

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

bank = tree_generator.generate_bank_from_pfsta(CHILDES_mle_pfsta, 100, 6)

print('--Treebank--')
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

# mle_likelihood = likelihood_no_order(CHILDES_mle_pfsta, bank)
# print('Likelihood with MLE PFSTA:', mle_likelihood, '\n')

p = PFSTA()
over_under.initialize_random(p, 4, ['WH', 'V', 'X', 'NP'])
st = time.time()
new_p, likelihood = update_no_order_until_pen(p, bank, 0.1)
new_p.print()
new_p.pretty_print(assignment)
et = time.time()

# print(et-st)

