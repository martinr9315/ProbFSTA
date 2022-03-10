from pfsta import PFSTA, Node
import over_under
from expectation_maximization import ObservedEvents, expectations_from_observation, sum_counts
# -------------------Testing------------


root1 = Node('a')
root1.set_address('')
root1.children = [Node('b'), Node('c')]
root1.children[1].children = [Node('d'), Node('e')]
over_under.assign_addresses(root1)
# print(get_address_list(root1))
# trees = read_trees("test_trees.parsed")

pfsta1 = PFSTA([1, 2, 3],
               {1: 1.0},
               {(1, 'a', (2)): 0.2,
                (1, 'a', (2, 2)): 0.3,
                (2, 'c', (3, 3)): 0.2,
                (2, 'b', ()): 0.1,
                (3, 'd', ()): 0.1,
                (3, 'e', ()): 0.1})

pfsta2 = PFSTA([1, 2, 3],
               {1: 1.0},
               {(1, 'a', (2)): 0.2,
                (1, 'a', (1, 2)): 0.3,
                (2, 'c', (2, 3)): 0.2,
                (2, 'b', ()): 0.1,
                (3, 'd', ()): 0.1,
                (3, 'e', ()): 0.1})

# print(over_under.prob_under(pfsta1, root1, 1))
# print(prob_over(pfsta1, get_context(root1, "0"), 2))

# print(tree_prob_via_under(pfsta1, root1))
# print(tree_prob_via_over(pfsta1, root1))

observed = ObservedEvents(root1)
# observed.print()
# observed.start_event.print()

result = expectations_from_observation(pfsta1, observed)
for r in result:
    r.print()

# (sum_counts(result)).print()