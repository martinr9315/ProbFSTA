from PFSTA import PFSTA
from tree_generator import generate_bank_from_pfsta
from parsing import parse, split_bank, parse, depth_limit
from over_under import depth, get_terminals
import random, os
from collections import Counter


goal_pfsta = PFSTA(   [0, 1, 2, 3, 4],
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

goal_pfsta_2 = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'WH', ()): 1.0,
                         (1, '*', (0, 4)): 0.297,
                         (1, '*', (1, 1)): 0.2339,
                         (1, '*', (2, 3)): 0.2612,
                         (1, 'C', ()): 0.2079,
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
                         (1, 'C', ()): 0.5079,
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
                         (1, 'C', ()): 0.6179,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (2,)): 0.5122,    # unary branching for unlicensed V
                         (4, '*', (1, 4)): 0.4878})

goal_pfsta_5 = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'WH', ()): 1.0,
                         (1, '*', (0, 4)): 0.017,
                         (1, '*', (1, 1)): 0.4479,
                         (1, '*', (2, 3)): 0.0332,
                         (1, 'C', ()): 0.4569,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (2,)): 0.5001,    # unary branching for unlicensed V
                         (4, '*', (1, 4)): 0.4999})

def avg_depth(bank):
    d = 0
    for t in bank:
        d += len(depth(t))
    return d/len(bank)

def print_stats(n, split_bank):
    for k, v in split_bank.items():
        print('\t', k+': %.2f' % (len(v)/n))

def count_transitions(bank):
    wh_count = 0
    np_count = 0
    c_only_count = 0
    for t in bank:
        terminals = Counter(get_terminals(t))
        wh_count += terminals['WH']
        np_count += terminals['NP']
        if 'NP' not in terminals.keys() and 'WH' not in terminals.keys():
            c_only_count += 1
    return {'WH transitions': wh_count, 'NP transitions': np_count, 'C only': c_only_count}

# stats - generated tree bank
# average depth
# number of V-NP trees
# number of Wh-V trees
# number of all C trees
# number of both trees

size = [100, 200]

for n in size:
    bank = generate_bank_from_pfsta(goal_pfsta_4, n, 10)
    split_bank_n = split_bank(bank)
    print('\n', n, 'generated trees')
    print_stats(n, split_bank_n)
    print('\t',count_transitions(bank))
    print('\t', 'avg WH depth: %.2f' % avg_depth(split_bank_n['wh']))
    print('\t', 'avg depth: %.2f' % avg_depth(bank))


# stats - CHILDES tree bank
# average depth
# number of V-NP trees
# number of Wh-V trees
# number of all C trees
# number of both trees


directory = 'CHILDESTreebank/hslld-hv1-er/'
filenames = ['CHILDESTreebank/brown-adam.parsed','CHILDESTreebank/valian+animacy+theta.parsed','CHILDESTreebank/brown-eve+animacy+theta.parsed']
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        filenames.append(f)
filenames.remove('CHILDESTreebank/hslld-hv1-er/.DS_Store')
CHILDES_bank = parse(filenames)
for n in size:
    bank = random.sample(CHILDES_bank, n)
    split_bank_n = split_bank(bank)
    print('\n', n, 'CHILDES trees')
    print_stats(n, split_bank_n)
    print(count_transitions(bank))
    print('\t', 'avg WH depth: %.2f' % avg_depth(split_bank_n['wh']))
    print('\t', 'avg depth: %.2f' % avg_depth(bank))

