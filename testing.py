
from pfsta import PFSTA, Node
import over_under
from expectation_maximization import (ObservedEvents, highest_likelihood,
                                      likelihood, update, update_n,
                                      update_no_order, update_until_stable)
import tree_generator
# -------------------Testing------------

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

# bank = tree_generator.generate_bank(['A', 'B', 'C'], 4, 50)
# for t in bank:
#     over_under.print_tree(t)
#     print("--")


trees = tree_generator.read_from_file("trees.txt")
# for t in bank:
#     over_under.assign_addresses(t)
#     over_under.print_tree(t)
#     print("--")

pfstas = [PFSTA()] * 10
new_pfstas = []
for i, p in enumerate(pfstas):
    over_under.initialize_random(p, 2, ['A', 'B', 'C'])
    # p.clean_print()
    new_p = update_n(p, trees, 20)
    print(i, likelihood(p, trees), '-->', likelihood(new_p, trees))
    new_pfstas.append(new_p)
    # new_p.clean_print()

best = highest_likelihood(new_pfstas, trees)
best.clean_print()


# p = PFSTA()
# over_under.initialize_random(p, 2, ['A', 'B', 'C'])
# print(likelihood(p, trees))
# print('________')
# p.clean_print()
# print('-->')
# new_p = update_n(p, trees, 20)
# print(likelihood(new_p, trees))
# print('________')
# new_p.clean_print()


debugNO_FSTA = PFSTA([0, 1],
                {0: 0.67, 1: 0.33},
                {(0, "*", (0, 0)): 0.4,
                (0, "*", (0, 1)): 0.52,
                (0, "*", (1, 1)): 0.03,
                (0, "A", ()): 0.03,
                (0, "B", ()): 0.02,
                (1, "C", ()): 1})


initial_debugging = PFSTA( [0, 1], 
{0: 0.67, 1:0.33},
  {(0, "*", (0, 1)): 0.5,
  (0, "*", (0, 0)): 0.4,
  (0, "*", (1, 0)): 0.02,
  (0, "*", (1, 1)): 0.03,
  (0, "A", ()): 0.03,
  (0, "B", ()): 0.02,
  ((1, "C", ())): 1},
)

# print(likelihood(initial_debugging, [tree1, tree2, tree1]))
# initial_debugging.clean_print()
# m = update_n(initial_debugging, [tree1, tree2, tree1], 50)
# m.clean_print()
# print(likelihood(m, [tree1, tree2, tree1]))



# why are likelihoods lower when states are assigned
# do i need to adjust tree bank when I assign states?
# why are likelihoods so low/so similar within a batch