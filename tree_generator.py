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


tree = random_tree(['*'], 3)
tree.set_address('')
over_under.assign_addresses(tree)
addy = over_under.get_address_list(tree)
