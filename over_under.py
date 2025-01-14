from PFSTA import PFSTA, Node, TreeContext
import itertools
import random
import numpy as np
#  ----------- PFSTA utilities -------------

NO_ORDER = True
ASSIGN_STATES = True   # assignments are hard coded for now
RESOLVED_DEPENDENCY = True  # initial state is 1 (neutral state)

def make_pfsta(values):
    pfsta = PFSTA(q=[0,1,2,3,4])
    state_seq = possible_lists_no_order(pfsta.q, 2)
    state_seq.update(possible_lists_no_order(pfsta.q, 1))
    to_normalize = [values[i:i+24] for i in range(0, 120, 24)]

    normalized_values = []
    for v in to_normalize:
        v = np.abs(np.array(v))
        total_sum = np.sum(v)
        normalized = v / total_sum
        normalized_values.append(normalized)
    for q in pfsta.q:
        j = 0 
        if q == 1:
            pfsta.i[q] = 1
        else:
            pfsta.i[q] = 0
        for st in state_seq:  # transition probabilities
            pfsta.delta[(q, '*', st)] = normalized_values[q][j]
            j += 1
        for t in ['WH', 'V', 'X', 'NP']:
            pfsta.delta[(q, t, ())] = normalized_values[q][j]
            j += 1
    return pfsta

def pfsta_values(pfsta):
    return list(pfsta.delta.values())


def initialize_random(pfsta, n, terminals):
    pfsta.q = list(range(n+1))
    if NO_ORDER:
        state_seq = possible_lists_no_order(pfsta.q, 2)
        state_seq.update(possible_lists_no_order(pfsta.q, 1))
    else:
        state_seq = possible_lists(pfsta.q, 2)
    seeds = random.sample(range(1, 100), len(pfsta.q))
    # print("Seeds:", seeds)
    for i, q in enumerate(pfsta.q):
        if RESOLVED_DEPENDENCY:
            if q == 1:
                pfsta.i[q] = 1
            else:
                pfsta.i[q] = 0
        else:
            random.seed(seeds[0])
            initial_random = random.sample(range(1, 100), len(pfsta.q))
            initial_sum = sum(initial_random)
            initial_probabilites = [(r/initial_sum) for r in initial_random]
            pfsta.i[q] = initial_probabilites[i]  # initial probabilities
        if q == 4:
            random.seed(seeds[q])
            delta_random = random.sample(range(1, 100), len(state_seq))
        elif ASSIGN_STATES:
            random.seed(seeds[q])
            delta_random = random.sample(range(1, 100), len(state_seq)+1)
        else:
            random.seed(seeds[q])
            delta_random = random.sample(range(1, 100), len(state_seq)+len(terminals))
        delta_sum = sum(delta_random)
        delta_probabilites = [(r/delta_sum) for r in delta_random]
        j = 0
        for st in state_seq:  # transition probabilities
            pfsta.delta[(q, '*', st)] = delta_probabilites[j]
            j += 1
        if ASSIGN_STATES:
            if q == 0:
                pfsta.delta[(q, 'WH', ())] = delta_probabilites[j]
                pfsta.delta[(q, 'X', ())] = 0.0
                pfsta.delta[(q, 'V', ())] = 0.0
                pfsta.delta[(q, 'NP', ())] = 0.0
            elif q == 1:
                pfsta.delta[(q, 'WH', ())] = 0.0
                pfsta.delta[(q, 'X', ())] = delta_probabilites[j]
                pfsta.delta[(q, 'V', ())] = 0.0
                pfsta.delta[(q, 'NP', ())] = 0.0
            elif q == 2:
                pfsta.delta[(q, 'WH', ())] = 0.0
                pfsta.delta[(q, 'X', ())] = 0.0
                pfsta.delta[(q, 'V', ())] = delta_probabilites[j]
                pfsta.delta[(q, 'NP', ())] = 0.0
            elif q == 3:
                pfsta.delta[(q, 'WH', ())] = 0.0
                pfsta.delta[(q, 'X', ())] = 0.0
                pfsta.delta[(q, 'V', ())] = 0.0
                pfsta.delta[(q, 'NP', ())] = delta_probabilites[j]
            elif q == 4:
                pfsta.delta[(q, 'WH', ())] = 0.0
                pfsta.delta[(q, 'X', ())] = 0.0
                pfsta.delta[(q, 'V', ())] = 0.0
                pfsta.delta[(q, 'NP', ())] = 0.0
        else:
            for t in terminals:  # terminal probabilities
                pfsta.delta[(q, t, ())] = delta_probabilites[j]
                j += 1

def initialize_goal(pfsta, n, terminals, goal):
    initialize_random(pfsta, n, terminals)
    # fix transitions
    for t,v in pfsta.delta.items():
        pfsta.delta[t] = goal.transition_prob(t)


#  ----------- Tree utilities -------------


def assign_addresses(node):
    for i, n in enumerate(node.children):
        if n:
            n.set_address(node.address+str(i))
            assign_addresses(n)


def get_label(root, address):  # getLabel
    node = root
    for num in address:
        node = node.children[int(num)]
    return (node.label)


def get_node(root, address):  # getSubTree
    node = root
    for num in address:
        node = node.children[int(num)]
    return node


def get_left_sis(root, address):  # getLeftSis
    if address == '':
        return None
    else:
        mother = get_node(root, address[:-1])
        left_sisters = []
        for n in mother.children:
            if n and (n.address < address):
                left_sisters.append(n)
        return left_sisters


def get_right_sis(root, address):  # getRightSis
    if address == '':
        return None
    else:
        mother = get_node(root, address[:-1])
        right_sisters = []
        for n in mother.children:
            if n and (n.address > address):
                right_sisters.append(n)
        return right_sisters

def get_sisters(root, address):
    if address == '':
        return None
    else:
        mother = get_node(root, address[:-1])
        sisters = []
        for n in mother.children:
            sisters.append(n.label)
        return sisters


def get_context(root, address):  # getCxt
    if address == '':
        root_context = TreeContext()
        root_context.set_root()
        return root_context
    mother = get_node(root, address[:-1])
    left_sisters = get_left_sis(root, address)
    right_sisters = get_right_sis(root, address)
    mother_context = get_context(root, address[:-1])
    context = TreeContext()
    context.set_context(mother, mother_context, left_sisters, right_sisters)
    return context


def get_address_list(node):
    result = []
    traverse(node, result)
    return result


def traverse(node, address_list):
    if not node:
        return
    address_list.append(node.address)
    # node.print_address()
    for n in node.children:
        traverse(n, address_list)


def count(node):
    if node:
        sum = 0
        for child in node.children:
            sum += count(child)
        return 1 + sum


def depth(node):
    addresses = get_address_list(node)
    return max(addresses, key=len)


def print_tree(node, f=None):
    if node:
        node.print_address(f)
        for n in node.children:
            print_tree(n, f)

def print_annotated_tree(node):
    if node:
        node.annotated_print()
        for n in node.children:
            print_annotated_tree(n)


def get_terminals(node):
    terminals = []
    recurse_terminals(node, terminals)
    return terminals


def recurse_terminals(node, terminals):
    if node:
        if node.get_label() != '*':
            terminals.append(node.get_label())
        for n in node.children:
            recurse_terminals(n, terminals)


def visual_print(node):
    addresses = sorted(get_address_list(node), key=len)
    curr_level = 0
    for a in addresses:
        if len(a) != curr_level:
            print('\n')
            curr_level = len(a)
        print(get_label(node, a), end="\t")


def clear_memos(trees):
    print("\t\t\t\tcleared")
    for t in trees:
        t.clear_tree_memos()

# -------------- Over/Under Utilities ---------------------------


def possible_lists(states, n):
    return set(list(itertools.permutations(states, n)) +
               list(itertools.combinations_with_replacement(states, n)))


def possible_lists_no_order(states, n):
    return set(list(itertools.combinations_with_replacement(states, n)))


def order(states, n):
    return set(list(itertools.permutations(states, n)))


def zip_three(s1, s2, s3):
    zipped = []
    for i1 in s1:
        for i2 in s2:
            for i3 in s3:
                zipped.append((i1, i2, i3))
    return zipped


def zip_two(s1, s2):
    zipped = []
    for i1 in s1:
        for i2 in s2:
            zipped.append((i1, i2))
    return zipped


def filter_through(stset, para):
    possible_states = list(itertools.permutations(stset))
    matches = []
    for s in possible_states:
        if s == para:
            matches.append(s)
    return matches

# ------------ Reading trees ------------------------


def read_trees(file):
    trees = []
    with open(file) as f:
        lines = f.read()
        lines = lines.split('\n\n\n')
        for l in lines:
            s = clean(l)
            string = split_into_nodes(s)
            root = tree_from_string(string, 0, len(string)-1)
            root.set_address('')
            assign_addresses(root)
            trees.append(root)
    return trees


def clean(s):
    to_remove = [" ", "\n", "(.?)", "(..)"]
    s = s[1:-1]
    for r in to_remove:
        s = s.replace(r, "")
    return s


def split_into_nodes(s):
    tree = []
    i = 0
    while i < len(s):
        label = ""
        if s[i] == ')' or s[i] == '(':
            tree.append(s[i])
            i += 1
        else:
            j = i
            while j < len(s) and s[j] != ')' and s[j] != '(':
                label += s[j]
                j += 1
            i = j
            tree.append(label)
    return tree


def find_index(s, si, ei):
    if (si > ei):
        return -1
    stack = []
    for i in range(si, ei + 1):
        if (s[i] == '('):
            stack.append(s[i])
        elif (s[i] == ')'):
            if (stack[-1] == '('):
                stack.pop(-1)
                if len(stack) == 0:
                    return i
    return -1


def tree_from_string(s, si, ei):
    if (si > ei):
        return None
    root = Node(s[si])
    index = -1
    if (si + 1 <= ei and s[si + 1] == '('):
        index = find_index(s, si + 1, ei)
    if (index != -1):
        root.children = [tree_from_string(s, si + 2, index-1),
                         tree_from_string(s, index + 2, ei-1)]
    return root


def star_nodes(node):
    if node and len(node.children) > 0:
        node.star_label()
        for i, n in enumerate(node.children):
            star_nodes(n)


# ---------------------Recursive Under & Over------------------------

def prob_under(pfsta, node, state):
    if pfsta.get_under(node, state):
        return pfsta.get_under(node, state)
    else:
        if not node.children:
            return pfsta.transition_prob((state, node.label, ()))
        else:
            k = len(node.children)
            state_seq = possible_lists(pfsta.q, k)
            sum = 0
            for st in state_seq:
                zipped = list(zip(node.children, st))
                product = pfsta.transition_prob((state, node.label, st)) 
                for z in zipped:
                    product *= prob_under(pfsta, z[0], z[1])
                sum += product
            pfsta.unders[(node, state)] = sum
            return sum


def prob_over(pfsta, context, state):
    if pfsta.get_over(context, state):
        return pfsta.get_over(context, state)
    else:
        if context.is_root():
            return pfsta.start_prob(state)
        else:
            mother_label = context.mother.label
            kl = len(context.left_sisters)
            kr = len(context.right_sisters)
            poss_list_left = possible_lists(pfsta.q, kl)
            poss_list_right = possible_lists(pfsta.q, kr)
            zipped = zip_three(poss_list_left, poss_list_right, pfsta.q)
            sum = 0
            for l_state_seq, r_state_seq, mom_state in zipped:
                product = pfsta.transition_prob((mom_state, mother_label, (l_state_seq+(state,)+r_state_seq)))
                if product:
                    product *= prob_over(pfsta, context.mother_context, mom_state)
                    left_under = 1
                    for i, l_sis in enumerate(context.left_sisters):
                        left_under *= prob_under(pfsta, l_sis, l_state_seq[i])
                    right_under = 1
                    for i, r_sis in enumerate(context.right_sisters):
                        right_under *= prob_under(pfsta, r_sis, r_state_seq[i])
                    product *= left_under * right_under
                sum += product
            pfsta.overs[(context, state)] = sum
            return sum

# ---------------------No Order Recursive Under & Over------------------------


def prob_under_no_order(pfsta, node, state):
    if pfsta.get_under(node, state):
        return pfsta.get_under(node, state)
    else:
        if not node.children:
            return pfsta.transition_prob((state, node.label, ()))
        else:
            k = len(node.children)
            state_seq = possible_lists_no_order(pfsta.q, k)  # orderless
            sum = 0
            for st in state_seq:
                # TODO: clean up this look up so matches prob_over_no_order
                if len(set(st)) > 1:  # if the states are not same
                    ordered_list = order(st, k)  # generate ordering 
                    trans_prob = 0
                    for ordered_pair in ordered_list:
                        if pfsta.transition_prob((state, node.label, ordered_pair)) != 0.0:
                            trans_prob = pfsta.transition_prob((state, node.label, ordered_pair))
                            break
                    # if ordered, sum accross ordering
                    pair_sum = 0
                    for ordered_pair in ordered_list:
                        zipped = list(zip(node.children, ordered_pair))
                        product = trans_prob
                        for z in zipped:
                            product *= prob_under_no_order(pfsta, z[0], z[1])  # where z[1] is tree and z[1] is a state
                        pair_sum += product
                    sum += pair_sum
                else:
                    zipped = list(zip(node.children, st))
                    product = pfsta.transition_prob((state, node.label, st))
                    for z in zipped:
                        product *= prob_under_no_order(pfsta, z[0], z[1])  # where z[1] is tree and z[1] is a state
                    sum += product
            pfsta.unders[(node, state)] = sum
            return sum


def prob_over_no_order(pfsta, context, state):
    if pfsta.get_over(context, state):
        return pfsta.get_over(context, state)
    else:
        if context.is_root():
            return pfsta.start_prob(state)
        else:
            mother_label = context.mother.label
            kl = len(context.left_sisters)
            kr = len(context.right_sisters)
            poss_list_sisters = possible_lists_no_order(pfsta.q, kl+kr)
            sum = 0
            for mom_state in pfsta.q:
                sum_here = 0
                for sis_state_seq in poss_list_sisters:
                    children = tuple(sorted(sis_state_seq+(state,)))
                    product = pfsta.transition_prob((mom_state, mother_label, (children)))
                    if product:
                        product *= prob_over_no_order(pfsta, context.mother_context, mom_state)
                        for i, sis in enumerate(context.left_sisters + context.right_sisters):
                            product *= prob_under_no_order(pfsta, sis, sis_state_seq[i])
                    sum_here += product
                sum += sum_here
            pfsta.overs[(context, state)] = sum
            return sum


# ---------------Tree probabilities------------

def tree_prob_via_under(pfsta, node):
    sum = 0
    for state in pfsta.q:
        sum += pfsta.start_prob(state)*prob_under(pfsta, node, state)
    return sum


def tree_prob_via_under_no_order(pfsta, node):
    sum = 0
    for state in pfsta.q:
        sum += pfsta.start_prob(state)*prob_under_no_order(pfsta, node, state)
    return sum


def tree_prob_via_over_no_order(pfsta, node):
    addresses = sorted(get_address_list(node))
    term = get_label(node, addresses[-1])
    sum = 0
    for state in pfsta.q:
        sum += pfsta.transition_prob((state, term, ()))*prob_over_no_order(pfsta, get_context(node, addresses[-1]), state)
    return sum


def tree_prob_via_over(pfsta, node):
    sum = 0
    for state in pfsta.q:
        sum += pfsta.start_prob(state)*prob_over(pfsta, get_context(node, ""), state)
    return sum


# ------------Interpretable values-------------

def bottom_up(pfsta):
    bottom_up_val = {}
    for state in pfsta.q:
        bottom_up_val[state] = [(transitions, pfsta.delta[transitions]) for transitions in pfsta.delta.keys() if state in transitions[2]]
    for state, transitions in bottom_up_val.items():
        curr = {}
        denom = 0
        for (tr, prob) in transitions:
            if state == tr[2][0]:
                curr[(tr[0], tr[1], ('_', tr[2][1]))] = prob
                denom += prob
            if state == tr[2][1]:
                curr[(tr[0], tr[1], (tr[2][0], '_'))] = prob
                denom += prob
        for i, prob in curr.items():
            curr[i] = prob/denom
        bottom_up_val[state] = curr
    return bottom_up_val
    


