from os import O_RDONLY
from pfsta import PFSTA, Node
import over_under
from expectation_maximization import (ObservedEvents, expectations_from_corpus,
                                      expectations_from_observation,
                                      estimate_from_counts, update)
# -------------------Testing------------


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

tree3 = Node('*')
tree3.children = [Node('*'), Node('A')]
tree3.children[0].children = [Node('C'), Node('B')]
tree3.set_address('')
over_under.assign_addresses(tree3)

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

expectations_from_corpus(debug_pfsta, [tree1, tree2]).print()

# (update(debug_pfsta, [tree1])).print()
# print(over_under.prob_under(pfsta1, root1, 1))
# print(prob_over(pfsta1, get_context(root1, "0"), 2))

# print(tree_prob_via_under(pfsta1, root1))
# print(tree_prob_via_over(pfsta1, root1))

# observed = ObservedEvents(root1)
# observed.print()
# observed.start_event.print()

# result = expectations_from_observation(pfsta1, observed)
# print(result)
# states = [1, 2, 3]
# pfsta2 = estimate_from_counts(states, result)
# for r in result:
#     r.print()


# HStart 0 : 0.19760479041916168
# HStart 1 : 0.8023952095808383
# HStep 0 * (0, 0) : 0.19760479041916165
# HStep 0 * (0, 1) : 0.0
# HStep 0 * (1, 0) : 0.0
# HStep 0 * (1, 1) : 1.0
# HStep 0 A () : 1.0
# HStep 0 B () : 0.0
# HStep 0 C () : 0.0

# HStep 1 * (0, 0) : 0.8023952095808383
# HStep 1 * (0, 1) : 0.0
# HStep 1 * (1, 0) : 0.0
# HStep 1 * (1, 1) : 0.0

# HStep 1 A () : 0.0
# HStep 1 B () : 1.0
# HStep 1 C () : 1.0



# expectations from observations tree 1 only
# HStart 0 : 0.19760479041916168
# HStart 1 : 0.8023952095808383
# HStep 0 * (0, 0) : 0.19760479041916165
# HStep 0 * (0, 1) : 0.0
# HStep 0 * (1, 0) : 0.0
# HStep 0 * (1, 1) : 0.0 --?
# HStep 0 A () : 1.0
# HStep 0 B () : 0.0
# HStep 0 C () : 0.0

# HStep 1 * (0, 0) : 0.8023952095808383
# HStep 1 * (0, 1) : 0.0
# HStep 1 * (1, 0) : 0.0
# HStep 1 * (1, 1) : 0.0
# HStep 1 A () : 0.0
# HStep 1 B () : 0.0 --?
# HStep 1 C () : 0.0 --?




# tree2 only
# HStart 0 : 0.10963455149501661
# HStart 1 : 0.8903654485049833
# HStep 0 * (0, 1) : 0.054817275747508304
# HStep 0 * (0, 0) : 0.054817275747508304
# HStep 0 * (1, 0) : 0.0
# HStep 0 * (1, 1) : 1.0 --?
# HStep 0 A () : 1.0
# HStep 0 B () : 0.0
# HStep 0 C () : 0.0

# HStep 1 * (0, 0) : 0.22259136212624583
# HStep 1 * (0, 1) : 0.6677740863787375
# HStep 1 * (1, 0) : 0.0
# HStep 1 * (1, 1) : 0.0 --?
# HStep 1 A () : 0.0
# HStep 1 B () : 0.0 --?
# HStep 1 C () : 0.0 --?

#tree 3 only
# HStart 0 : 0.19760479041916168
# HStart 1 : 0.8023952095808383
# HStep 0 * (0, 0) : 0.19760479041916165
# HStep 0 * (0, 1) : 0.0
# HStep 0 * (1, 0) : 0.0
# HStep 0 * (1, 1) : 0.0 --?
# HStep 0 A () : 1.0
# HStep 0 B () : 0.0
# HStep 0 C () : 0.0

# HStep 1 * (0, 0) : 0.8023952095808383
# HStep 1 * (0, 1) : 0.0
# HStep 1 * (1, 0) : 0.0
# HStep 1 * (1, 1) : 0.0
# HStep 1 A () : 0.0 
# HStep 1 B () : 0.0 --?
# HStep 1 C () : 0.0 --?

# b_context = over_under.get_context(tree1, "01")
# c_context = over_under.get_context(tree1, "00").print()
# print(over_under.tree_prob_via_under(debug_pfsta, tree1))
# print(over_under.tree_prob_via_over(debug_pfsta, tree1))
# print(over_under.prob_under(debug_pfsta, tree1.children[0], 0))

# print(over_under.prob_over(debug_pfsta, (over_under.get_context(tree1, "0")), 0))
# (update(debug_pfsta, [tree1, tree2])).print()

