from PFSTA import PFSTA
import over_under
from expectation_maximization import (  likelihood_no_order,
                                        update,
                                        update_no_order,
                                        update_no_order_n,
                                        update_no_order_until)
import tree_generator

# p = PFSTA()
# over_under.initialize_random(p, 4, ['Wh', 'V', 'C', 'NP'])
# p.clean_print()

goal_pfsta = PFSTA( [0, 1, 2, 3, 4],
                    {1: 1.0},
                    {(0, 'Wh', ()): 1.0,
                    (1, '*', (4, 0)): 0.0688,
                    (1, '*', (1, 1)): 0.2982,
                    (1, '*', (3, 2)): 0.2523,
                    (1, 'C', ()): 0.3807,
                    (2, 'V', ()): 1.0,
                    (3, 'NP', ()): 1.0,
                    (4, '*', (2, 1)): 0.6818,
                    (4, '*', (4, 1)): 0.3182})

goal_pfsta_3 = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'Wh', ()): 1.0,
                         (1, '*', (0, 4)): 0.097,
                         (1, '*', (1, 1)): 0.2239,
                         (1, '*', (2, 3)): 0.2612,
                         (1, 'C', ()): 0.4179,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (2,)): 0.7222,    # unary branching for unlicensed V
                         (4, '*', (1, 4)): 0.2778})

# ---------------------------------------------------------------------------------

# # depth 4 tree with V licensed by Wh at bottom level
# sproblem_tree = tree_generator.read_from_file("treebanks/debugging/problem_tree.txt")
# over_under.print_tree(problem_tree[0])

# # ordered update on problem tree - succeeds

# print("running ordered update on problem tree...")
# over_under.print_tree(problem_tree[0])
# update(goal_pfsta, problem_tree)
# print("problem_tree ordered update succeeded\n")

# # ---------------------------------------------------------------------------------


def test_update(tree_file):
    tree = tree_generator.read_from_file("treebanks/debugging/"+tree_file)
    print(tree_file + " unordered update...")
    # over_under.print_tree(tree[0])
    update_no_order_until(goal_pfsta, tree, .5)
    print(tree_file + " unordered update succeeded\n")
    # print_all_overs(tree, True)


def print_all_overs(tree, non_zero):
    # print('over value for each node of problem tree:')
    for t in tree:
        addresses = over_under.get_address_list(t)
        for a in addresses:
            for q in goal_pfsta.q:
                over_value = over_under.prob_over_no_order(goal_pfsta, over_under.get_context(t, a), q)
                if not non_zero or over_value != 0:
                    print('address:', a, '\tstate:', q, ':', over_value)
                # print('address:', a, '\tstate:', q, ':', over_under.prob_under_no_order(goal_pfsta, over_under.get_node(t, a), q))


# test_update('prob_flipped.txt')
# test_update('50_free_depth.txt')
# print(over_under.failed_transitions)


# matching over and under probs!
bank = tree_generator.read_from_file("treebanks/debugging/new_prob_tree.txt")
for i, t in enumerate(bank):
    print('---', i+1)
    print(over_under.tree_prob_via_over_no_order(goal_pfsta_3, t))
    print(over_under.tree_prob_via_under_no_order(goal_pfsta_3, t))
