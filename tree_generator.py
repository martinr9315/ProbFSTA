from PFSTA import Node
import random
import over_under
import copy

# done:
#   A and B are not siblings
#   global variables for n-nary, A c-commands B (only one A/B), A-B siblings

N_ARY = 2  # max children generated node can have
C_COMMAND = True  # enforce A c-commands B (only one A/B)
NOT_SIBLINGS = 0  # enforce A-B are allowed to be siblings only x% of the time

# 10/17: either A must c-command V or V is siblings with NP


def read_from_file(file):
    f = open(file, "r")
    str = (f.read()).split('--')
    trees = []
    for s in str:
        if s:
            trees.append(read_from_addresses(s))
    for t in trees:
        over_under.assign_addresses(t)
    return trees


def read_from_addresses(s):
    s = s.split()
    s = sorted(s, key=len)
    tree = Node()
    tree.set_address('')
    for a in s[1:]:
        over_under.assign_addresses(tree)
        info = a.split(":")
        address = info[0]
        label = info[1]
        mother = over_under.get_node(tree, address[:-1])
        (mother.children).append(Node(label))
    return tree


def random_tree(alphabet, depth):
    if depth:
        root = Node(random.choice(alphabet))
        node = root
        if depth != 1:
            number_children = random.choice([0, N_ARY, N_ARY])
        else:
            number_children = 0
        if (number_children > 0):
            node.star_label()
        for n in range(number_children):
            node.children.append(random_tree(alphabet, depth-1))
        return root


def not_siblings(tree):
    addresses = over_under.get_address_list(tree)
    a_address = ""
    b_address = ""
    for a in addresses:
        if over_under.get_label(tree, a) == 'Wh':
            a_address = a
        elif over_under.get_label(tree, a) == 'V':
            b_address = a
    if len(a_address) == len(b_address):
        # percent = random.choice(range(10))
        # if percent < (NOT_SIBLINGS * 10):
        #     return True
        return False
    return True


def siblings(tree):
    addresses = over_under.get_address_list(tree)
    for a in addresses:
        if over_under.get_label(tree, a) == 'V':
            sis = over_under.get_sis(tree, a)
            if over_under.get_label(tree, sis) != 'NP':
                return False
        elif over_under.get_label(tree, a) == 'NP':
            sis = over_under.get_sis(tree, a)
            if (sis is None) or (over_under.get_label(tree, sis) != 'V'):
                return False
    return True


def one_licensor(tree):
    # make sure tree only contains either A or NP
    addresses = over_under.get_address_list(tree)
    labels = []
    for a in addresses:
        if over_under.get_label(tree, a) == 'Wh':
            labels.append('Wh')
        if over_under.get_label(tree, a) == 'NP':
            labels.append('NP')
    if ('Wh' in labels) and ('NP' not in labels):
        return 'Wh'
    elif ('Wh' not in labels) and ('NP' in labels):
        return 'NP'
    return ''


def c_command(tree):
    # make sure A c-commands V
    addresses = over_under.get_address_list(tree)
    a_count = 0
    a_address = ""
    b_count = 0
    b_address = ""
    for a in addresses:
        if over_under.get_label(tree, a) == 'Wh':
            a_count += 1
            a_address = a
        elif over_under.get_label(tree, a) == 'V':
            b_count += 1
            b_address = a
    if a_count != 1 or b_count != 1:
        return False

    if ((b_address[:len(a_address)] != a_address) and  # Node A does not dominate B, 
       (a_address[:len(b_address)] != b_address)):     # B does not dominate A, and
        a_mother_address = a_address[:-1]
        if b_address[:len(a_mother_address)] == a_mother_address:  # The first branching node that dominates A also dominates B
            return True
    return False


def generate_bank(alphabet, depth, n):
    bank = []
    count = 0
    while count < n:
        t = random_tree(alphabet, depth)
        t.set_address('')
        over_under.assign_addresses(t)
        if C_COMMAND:
            licensor = one_licensor(t)
            if licensor == 'Wh':
                if c_command(t) and not_siblings(t):
                    count += 1
                    bank.append(t)
            elif licensor == 'NP' and siblings(t):
                count += 1
                bank.append(t)
        else:
            count += 1
            bank.append(t)
    return bank


def generate_bank_from_pfsta(pfsta, n):
    bank = []
    for _ in range(n):
        root = Node(state=random.choice(list(pfsta.i.keys())))
        bank.append(generate_tree_from_pfsta(pfsta, root, 3))
    return bank


def generate_tree_from_pfsta(pfsta, node, depth):
    if depth:
        for c in node.children:
            generate_tree_from_pfsta(pfsta, c, depth-1)
        return node


def produce_transition(pfsta, node):
    possible_transitions = pfsta.possible_transitions(node.state)
    weights = [v for k, v in possible_transitions.items()]
    transition = random.choices(possible_transitions, weights=weights)
    children = []
    node.label = transition[1]
    if node.label == "*":
        for c in transition[2]:
            children.append(Node(state=c))
    node.children = children


# ------------Changing geometry------------
def gap_rotation(bank):
    tree = copy.deepcopy(bank)
    for i in tree:
        addresses = over_under.get_address_list(i)
        i.set_address('')
        for a in addresses:
            if over_under.get_label(i, a) == 'B':
                tr = Node()
                tr.label = 'V'
                node = over_under.get_node(i, a)
                node.star_label()
                node.children = [tr]
        over_under.assign_addresses(i)
    return tree


def trans_rotation(bank):
    tree = copy.deepcopy(bank)
    for i in tree:
        addresses = over_under.get_address_list(i)
        i.set_address('')
        for a in addresses:
            if over_under.get_label(i, a) == 'A':
                node = over_under.get_node(i, a)
                node.label = 'C'
            elif over_under.get_label(i, a) == 'B':
                tr = Node()
                tr.label = 'V'
                tr1 = Node()
                tr1.label = 'NP'
                node = over_under.get_node(i, a)
                node.star_label()
                node.children = [tr, tr1]
        over_under.assign_addresses(i)
    return tree 
                


    