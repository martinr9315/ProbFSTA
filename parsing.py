from trees import get_trees
from PFSTA import Node, PFSTA
from over_under import (assign_addresses, print_tree, get_sisters, get_address_list, get_node,
                       star_nodes, tree_prob_via_over_no_order, tree_prob_via_under_no_order)
import signal


VERB_LABELS = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'COP']

p = PFSTA(  [0, 1, 2, 3, 4],
                {1: 1.0},
                {(0, 'Wh', ()): 1.0,
                    (1, '*', (0, 4)): 0.097,
                    (1, '*', (1, 1)): 0.2239,
                    (1, '*', (2, 3)): 0.2612,
                    (1, 'C', ()): 0.4179,
                    (2, 'V', ()): 1.0,
                    (3, 'NP', ()): 1.0,
                    (4, '*', (2,)): 0.7222,    # unary branching for unlicensed V
                    (4, '*', (1, 4)): 0.2778})

f = open('CHILDESTreebank/brown-adam.parsed', "r")
trees = get_trees(f)

def from_tuple(t):
    if not isinstance(t, tuple):
        return Node(t)
    if len(t) > 0:
        return Node(t[0], children=[from_tuple(x) for x in t[1:]])


def clean_verbs(root):
    addresses = get_address_list(root)
    for a in addresses:
        n = get_node(root, a)
        if n.get_label() in VERB_LABELS:
            n.set_label('V')
            sisters = get_sisters(root, a)
            if 'NP' not in sisters:
                n.set_label('C')
        elif n.get_label() == 'NP':
            # n.print()
            sisters = get_sisters(root, a)
            if 'V' not in sisters:
                n.set_label('C')
        else:
            n.set_label('C')


def binarize(node):
    if not node.children:
        return node
    left = binarize(node.children[0])
    right = binarize(node.children[1]) if len(node.children) > 1 else None
    if right:
        return Node(node.label, children=[left, right])
    return Node(node.label, children=[left])


def collapse_unary(node):
    if not node.children:
        return node
    if len(node.children) == 1 and node.label == node.children[0].label:
        return collapse_unary(node.children[0])
    elif node.label in ['V', 'NP']:
        node.children = []
    else:
        for i, child in enumerate(node.children):
            node.children[i] = collapse_unary(child)
    return node


def timeout_handler(signum, frame):
    raise TimeoutError("Computation timed out.")

timeouts = []

for i, t in enumerate(trees[:100]):
    if 'FRAG' not in str(t) and 'SBARQ' not in str(t): 
        print(i, t)
        print('-')
        tuple_tree = from_tuple(t)              # convert from tuple to tree
        binary_tree = binarize(tuple_tree)      # binarize tree
        binary_tree.set_address('')
        assign_addresses(binary_tree)

        clean_verbs(binary_tree)                # rewrite V w/o NP sister as C

        tree = collapse_unary(binary_tree)      # collapse unary branches (w/ same label) and complex V,NP
        tree.set_address('')
        assign_addresses(tree)

        star_nodes(tree)                        # star all inner nodes

        print_tree(tree)
        print('-')

        time_limit = 120                         # set the time limit in seconds
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(time_limit)
        try:
            prob = tree_prob_via_over_no_order(p, tree)
            # print(tree_prob_via_under_no_order(p, tree))
        except TimeoutError as e:
            print(e)
            timeouts.append((i,t))
            continue
        else:
            print(prob)
        finally:
            signal.alarm(0)

        assert prob != 0                        # make sure all trees are possible with goal PFSTA
        print('--\n')


print('Timed out on: ', timeouts)





# check: are only SBARQ wh sentences 


# is this an issue
# 1128 
# (ROOT
#   (S
#     (NP
#       (PRP it))
#     (VP
#       (AUX does)
#       (VP
#         (VB look)
# 	(PP
# 	  (IN like)
# 	  (NP
# 	    (NN part)
# 	    (PP
# 	      (IN of)
# 	      (NP
# 	        (DT an)
# 		(NN apple))))))))
#   (CC but)
#   (S
#     (NP
#       (PRP it))
#     (VP
#       (COP 's)
#       (NOT not))
#     (. .))))

# :*
# 0:*
# 00:C
# 01:*
# 010:C
# 011:*
# 0110:C
# 0111:*
# 01110:C
# 01111:*
# 011110:C
# 011111:*
# 0111110:C
# 0111111:*
# 01111110:C
# 01111111:C
# 1:C