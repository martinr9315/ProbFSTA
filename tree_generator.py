from pfsta import Node
import random
import over_under


def random_tree(alphabet, depth):
    if depth:
        root = Node(random.choice(alphabet))
        node = root
        for _ in range(depth):
            number_children = random.choice(range(2))
            for n in range(number_children):
                node.children.append(random_tree(alphabet, depth-1))
        return root


tree = random_tree(['a', 'b', 'c', 'd', 'e'], 3)
tree.set_address('')
over_under.assign_addresses(tree)
addy = over_under.get_address_list(tree)
