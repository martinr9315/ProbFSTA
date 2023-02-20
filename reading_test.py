from PFSTA import PFSTA
import over_under
import tree_generator


goal_pfsta = PFSTA(   [0, 1, 2, 3, 4],
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


bank = tree_generator.read_from_file("treebanks/debugging/problem_tree.txt")
for i, t in enumerate(bank):
    print('---', i+1)
    over_under.print_tree(t)
    print('under prob:', over_under.tree_prob_via_over_no_order(goal_pfsta, t))
    # print(over_under.tree_prob_via_under_no_order(goal_pfsta, t))