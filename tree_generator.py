from pfsta import Node
import random
import over_under

#TODO:
# read in tree from address list (text file)
# 


def random_tree(alphabet, depth):
    if depth:
        root = Node(random.choice(alphabet))
        node = root
        if depth != 1:
            number_children = random.choice(range(4))
        else:
            number_children = 0
        if (number_children > 0):
            node.star_label()
        for n in range(number_children):
            node.children.append(random_tree(alphabet, depth-1))
        return root


def c_command(tree):
    # make sure A c-commands B
    addresses = over_under.get_address_list(tree)
    a_count = 0
    a_address = ""
    b_count = 0
    b_address = ""
    for a in addresses:
        if over_under.get_label(tree, a) == 'A':
            a_count += 1
            a_address = a
        elif over_under.get_label(tree, a) == 'B':
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
        if c_command(t):
            count += 1
            bank.append(t)
    return bank
    