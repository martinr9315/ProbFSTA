from PFSTA import PFSTA, Node
from over_under import (assign_addresses, print_annotated_tree, print_tree,
                        get_address_list, get_node)
from parsing import parse
import os

def pfsta_mle(treebank):
    goal_pfsta = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'WH', ()): 1,
                         (1, '*', (0, 4)): 1,
                         (1, '*', (1, 1)): 1,
                         (1, '*', (2, 3)): 1,
                         (1, 'X', ()): 1,
                         (2, 'V', ()): 1,
                         (3, 'NP', ()): 1,
                         (4, '*', (2,)): 1,    
                         (4, '*', (1, 4)): 1})
    for i, t in enumerate(treebank):
        t.set_address('')
        assign_addresses(t)
        addresses = (sorted(get_address_list(t), key=len))
        addresses.reverse()
        for a in addresses: 
            n = get_node(t, a)
            if n.get_label() != '*':
                annotation = goal_pfsta.get_state((n.get_label(), ()))
                n.set_state(annotation)
                goal_pfsta.delta[(annotation, n.get_label(), ())] += 1
            else:
                child_states = [c.get_state() for c in n.children]
                child_states.sort()
                annotation = goal_pfsta.get_state(('*', tuple(child_states)))
                n.set_state(annotation)
                if annotation == None:
                    print_tree(t)
                    print('annotated:')
                    print_annotated_tree(t)
                    return 0
                else:
                    goal_pfsta.delta[(annotation,'*', tuple(child_states))] += 1

    for q in goal_pfsta.q: # normalize
        total = 0
        for k, v in goal_pfsta.delta.items():
            if k[0] == q: 
                total += v
        for k, v in goal_pfsta.delta.items():
            if k[0] == q:
                frac = v/total
                goal_pfsta.delta[k] = frac
    return goal_pfsta

# testing 
# tree1 = Node('*')
# tree1.children = [Node('V'), Node('NP')]
# tree1.set_address('')
# assign_addresses(tree1)
# pfsta_mle([tree1])
# print_annotated_tree(tree1)

directory = 'CHILDESTreebank/hslld-hv1-er/'
filenames = ['CHILDESTreebank/brown-adam.parsed','CHILDESTreebank/valian+animacy+theta.parsed','CHILDESTreebank/brown-eve+animacy+theta.parsed']
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        filenames.append(f)
filenames.remove('CHILDESTreebank/hslld-hv1-er/.DS_Store')
CHILDES_bank = parse(filenames)
p = pfsta_mle(CHILDES_bank)
p.clean_print()

#                       :None, *
#          0:None, *                         1:4, *
# 00:0, WH      01:1, *                 10:1, C      11:4, *
#           010:1, C 011:1, C                       110:2, V





