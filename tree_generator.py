from pfsta import Node
import random
import over_under


def random_tree(alphabet, depth):
    if depth:
        root = Node(random.choice(alphabet))
        node = root
        number_children = random.choice(range(4))
        for n in range(number_children):
            node.children.append(random_tree(alphabet, depth-1))
        return root


def generate_bank(alphabet, depth, n):
    bank = []
    for _ in range(n):
        t = random_tree(alphabet, depth)
        t.set_address('')
        over_under.assign_addresses(t)
        bank.append(t)
    return bank


def remove_inner_node_labels(bank):
    for tree in bank:
        over_under.star_nodes(tree)