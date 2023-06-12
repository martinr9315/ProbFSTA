from expectation_maximization import    (SoftCounts, HiddenEvent, maximize_from_counts_pen, likelihood_counts, likelihood_no_order, entropy_penalty_2)
from PFSTA import PFSTA
from over_under import (print_tree, initialize_random, pfsta_values)
import tree_generator
from mle import pfsta_mle, annotate
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

bank = tree_generator.generate_bank_from_pfsta(CHILDES_mle_pfsta, 10, 6)

print('--Treebank--')
for t in bank:
    print_tree(t)
    print('---')

# annotate trees 
counts_pfsta = annotate(bank)
counts_pfsta.print()

soft_counts = SoftCounts()
for state in counts_pfsta.q:
    h_event = HiddenEvent()
    h_event.set_start(state)
    if state == 1:
        soft_counts.hidden_events[h_event] = len(bank)
    else:
        soft_counts.hidden_events[h_event] = 0

for t, v in counts_pfsta.delta.items():
    h_event = HiddenEvent()
    h_event.set_transition(t[0], t[1], t[2])
    soft_counts.hidden_events[h_event] = v
    
soft_counts.print()


mle = pfsta_mle(bank)
print('MLE PFSTA')
mle.print()


print('likelihood of counts w/ MLE pfsta', likelihood_counts(mle,soft_counts))
print('likelihood of bank w/ MLE pfsta', likelihood_no_order(mle,bank))


p = PFSTA()
initialize_random(p, 4, ['WH', 'V', 'X', 'NP'])
maxed_p = maximize_from_counts_pen(soft_counts)
print('Optimized PFSTA')
maxed_p.clean_print()

print('likelihood of counts w/ maxed pfsta', likelihood_counts(maxed_p,soft_counts))
print('likelihood of bank w/ maxed pfsta', likelihood_no_order(maxed_p,bank))


# from scipy.stats import entropy
# pk = np.array(pfsta_values(p))
# H = entropy(pk)
# print(H)
# pk2 = np.array(pfsta_values(maxed_p))
# H2 = entropy(pk2)
# print(H2)


# H = entropy_penalty_2(p)
# print(H)
# H2 = entropy_penalty_2(maxed_p)
# print(H2)