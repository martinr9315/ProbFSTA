
from pfsta import Node, TreeContext
import itertools
import random

#  ----------- PFSTA utilities -------------
# Done: randomly initialize pfsta - binary (for now )
# assign state to A, B, and C
# insensitive to ordering
# all trees have resolved dependencies (initial state is C state)

NO_ORDER = False
ASSIGN_STATES = True    # assignments are hard coded for now
RESOLVED_DEPENDENCY = False  # initial state is C (2) state for all trees


def initialize_random(pfsta, n, terminals):
    pfsta.q = list(range(n+1))
    if NO_ORDER:
        state_seq = possible_lists_no_order(pfsta.q, n)
    else:
        state_seq = possible_lists(pfsta.q, n)
    initial_random = random.sample(range(0, 100), len(pfsta.q))
    initial_sum = sum(initial_random)
    initial_probabilites = [(r/initial_sum) for r in initial_random]
    for i, q in enumerate(pfsta.q):
        if RESOLVED_DEPENDENCY:
            pfsta.i[0] = 0
            pfsta.i[1] = 0
            pfsta.i[2] = 1
        else:
            pfsta.i[q] = initial_probabilites[i]  # initial probabilities
        if ASSIGN_STATES:
            delta_random = random.sample(range(0, 100), len(state_seq)+1)
        else:
            delta_random = random.sample(range(0, 100), len(state_seq)+len(terminals))
        delta_sum = sum(delta_random)
        delta_probabilites = [(r/delta_sum) for r in delta_random]
        j = 0
        for st in state_seq:  # transition probabilities
            pfsta.delta[(q, '*', st)] = delta_probabilites[j]
            j += 1
        if ASSIGN_STATES:
            if q == 0:
                pfsta.delta[(q, 'A', ())] = delta_probabilites[j]
                pfsta.delta[(q, 'B', ())] = 0.0
                pfsta.delta[(q, 'C', ())] = 0.0
            elif q == 1:
                pfsta.delta[(q, 'B', ())] = delta_probabilites[j]
                pfsta.delta[(q, 'A', ())] = 0.0
                pfsta.delta[(q, 'C', ())] = 0.0
            elif q == 2:
                pfsta.delta[(q, 'C', ())] = delta_probabilites[j]
                pfsta.delta[(q, 'A', ())] = 0.0
                pfsta.delta[(q, 'B', ())] = 0.0
        else:
            for t in terminals:  # terminal probabilities
                pfsta.delta[(q, t, ())] = delta_probabilites[j]
                j += 1
    
#  ----------- Tree utilities -------------
# Done: poss list no order, under no order, over no order


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
    return (node)


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
    # node.print_address()  # uncomment to s tree
    for n in node.children:
        traverse(n, address_list)


def print_tree(node):
    if node:
        node.print_address()
        for n in node.children:
            print_tree(n)

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
    if node and len(node.children)>0:
        node.star_label()
        for i, n in enumerate(node.children):
            star_nodes(n)


# ---------------------Recursive Under & Over------------------------

def prob_under(pfsta, node, state):
    if node.get_under(state):
        return node.get_under(state)
    else:
        if not node.children:
            return pfsta.transition_prob((state, node.label, ()))
        else:
            k = len(node.children)
            state_seq = possible_lists(pfsta.q, k)
            sum = 0
            for st in state_seq:
                zipped = list(zip(node.children, st))
                # this is where to fix for no order
                product = pfsta.transition_prob((state, node.label, st)) 
                for z in zipped:
                    product *= prob_under(pfsta, z[0], z[1])
                sum += product
            node.under[state] = sum
            return sum


def prob_over(pfsta, context, state):
    if context.get_over(state):
        return context.get_over(state)
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
            context.over[state] = sum
            return sum

# ---------------------No Order Recursive Under & Over------------------------


def prob_under_no_order(pfsta, node, state):
    if node.get_under_no_order(state):
        return node.get_under_no_order(state)
    else:
        if not node.children:
            return pfsta.transition_prob((state, node.label, ()))
        else:
            k = len(node.children)
            state_seq = possible_lists_no_order(pfsta.q, k)  # orderless
            sum = 0
            for st in state_seq:
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
            node.under_no_order[state] = sum
            return sum


def prob_over_no_order(pfsta, context, state):
    if context.get_over_no_order(state):
        return context.get_over_no_order(state)
    else:
        if context.is_root():
            return pfsta.start_prob(state)
        else:
            mother_label = context.mother.label
            kl = len(context.left_sisters)
            kr = len(context.right_sisters)
            poss_list_sisters = possible_lists_no_order(pfsta.q, kl+kr)
            zipped = list(zip(poss_list_sisters, pfsta.q))
            sum = 0
            for sis_state_seq, mom_state in zipped:
                ordered_sis_states = order(sis_state_seq, kl+kr)  # generate ordering 
                trans_prob = 0
                for ordered_list in ordered_sis_states:
                    children = ordered_list[:kl]+(state,)+ordered_list[kl:]
                    if pfsta.transition_prob((mom_state, mother_label, (children))):
                        trans_prob = pfsta.transition_prob((mom_state, mother_label, (children)))
                for ordered_list in ordered_sis_states:
                    product = trans_prob
                    if product:
                        product *= prob_over_no_order(pfsta, context.mother_context, mom_state)
                        left_under = 1
                        for i, l_sis in enumerate(context.left_sisters):
                            left_under *= prob_under_no_order(pfsta, l_sis, sis_state_seq[i])
                        right_under = 1
                        for i, r_sis in enumerate(context.right_sisters):
                            right_under *= prob_under_no_order(pfsta, r_sis, sis_state_seq[i+kl])
                        product *= left_under * right_under
                    sum += product
            context.over_no_order[state] = sum
            return sum


# ---------------Tree probabilities------------

def tree_prob_via_under(pfsta, node):
    sum = 0
    for state in pfsta.q:
        sum += pfsta.start_prob(state)*prob_under(pfsta, node, state)
    return sum


def tree_prob_via_over(pfsta, node):
    sum = 0
    for state in pfsta.q:
        sum += pfsta.start_prob(state)*prob_over(pfsta, get_context(node, ""), state)
    return sum