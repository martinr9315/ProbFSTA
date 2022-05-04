from pfsta import PFSTA, Node
import over_under
from expectation_maximization import (ObservedEvents, expectations_from_corpus,
                                      expectations_from_observation,
                                      estimate_from_counts, update)
import tree_generator
# -------------------Testing------------
#TODO: randomly initialize pfsta - binary (for now )

# root1 = Node('a')
# root1.set_address('')
# root1.children = [Node('b'), Node('c')]
# root1.children[1].children = [Node('d'), Node('e')]
# over_under.assign_addresses(root1)
# print(get_address_list(root1))
# trees = read_trees("test_trees.parsed")

tree1 = Node('*')
tree1.children = [Node('*'), Node('A')]
tree1.children[0].children = [Node('C'), Node('B')]
tree1.set_address('')
over_under.assign_addresses(tree1)

tree2 = Node('*')
tree2.children = [Node('A'), Node('*')]
tree2.children[1].children = [Node('B'), Node('C')]
tree2.set_address('')
over_under.assign_addresses(tree2)

# pfsta1 = PFSTA([1, 2, 3],
#                {1: 1.0},
#                {(1, 'a', (2)): 0.2,
#                 (1, 'a', (2, 2)): 0.3,
#                 (2, 'c', (3, 3)): 0.2,
#                 (2, 'b', ()): 0.1,
#                 (3, 'd', ()): 0.1,
#                 (3, 'e', ()): 0.1})

debug_pfsta = PFSTA([0, 1],
                    {0: 0.33, 1: 0.67},
                    {(0, "*", (0, 0)): 0.1,
                    (0, "*", (0, 1)): 0.05,
                    (0, "*", (0, 2)): 0.04,
                    (0, "*", (1, 1)): 0.01,
                    (0, "*", (1, 2)): 0.2,
                    (0, "*", (2, 2)): 0.5,
                    (0, "A", ()): 0.1,
                    (1, "*", (0, 0)): 0.2,
                    (1, "*", (0, 1)): 0.3,
                    (1, "*", (0, 2)): 0.01,
                    (1, "*", (1, 1)): 0.02,
                    (1, "*", (1, 2)): 0.07,
                    (1, "*", (2, 2)): 0.2,
                    (1, "B", ()): 0.1,
                    (1, "C", ()): 0.1})

# expectations_from_corpus(debug_pfsta, [tree1, tree2]).print()

# update(debug_pfsta, [tree1, tree2]).print()

print(over_under.prob_under_no_order(debug_pfsta, tree1, 1))

# tree_generator.c_command(tree2)

# bank = tree_generator.generate_bank(['A', 'B', 'C'], 4, 50)
# for t in bank:
#     over_under.print_tree(t)
#     print("--")

# trees = tree_generator.read_from_file("trees.txt")
# for t in trees:
#     over_under.assign_addresses(t)
#     over_under.print_tree(t)
# #     print("--")
# print(over_under.possible_lists_no_order(pfsta1, 2))
# print(over_under.possible_lists(pfsta1, 2))