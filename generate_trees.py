from PFSTA import PFSTA
import tree_generator
import over_under

goal_pfsta_1 = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'Wh', ()): 1.0,
                         (1, '*', (0, 4)): 0.0688,
                         (1, '*', (1, 1)): 0.2982,
                         (1, '*', (2, 3)): 0.2523,
                         (1, 'C', ()): 0.3807,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (1, 2)): 0.6818,
                         (4, '*', (1, 4)): 0.3182})

goal_pfsta_2 = PFSTA(   [0, 1, 2, 3, 4],
                        {1: 1.0},
                        {(0, 'Wh', ()): 1.0,
                         (1, '*', (0, 4)): 0.097,
                         (1, '*', (1, 1)): 0.2239,
                         (1, '*', (2, 3)): 0.2612,
                         (1, 'C', ()): 0.4179,
                         (2, 'V', ()): 1.0,
                         (3, 'NP', ()): 1.0,
                         (4, '*', (1, 2)): 0.7222,
                         (4, '*', (1, 4)): 0.2778})

num_trees = int(input("How many trees would you like to generate?  "))
enforce_depth = input("Would you like to enforce a maximum depth? (y/n) ")
enforce_depth = True if enforce_depth == 'y' else False
max_depth = None
if enforce_depth:
    max_depth = int(input("\tMax depth: "))

write_to_file = input("Write trees to file? (y/n)  ")
write_to_file = True if write_to_file == 'y' else False
f = None
if write_to_file:
    filename = input("\tInput file name: ")
    f = open('treebanks/'+filename, "x")

print("\nGenerating", num_trees, "trees...\n")
bank = tree_generator.generate_bank_from_pfsta(goal_pfsta_2, num_trees, max_depth)
for t in bank:
    over_under.print_tree(t, f)
    print("--")
    if f is not None:
        print("--", file=f)

if f is not None:
    f.close()
