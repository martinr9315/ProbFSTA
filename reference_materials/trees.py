
import re

from functools import reduce

# A tree is just a tuple of length >=2. 
# The first element must be a string, this is the root label. 
# Additional elements are daughters.
#   - If there is only one daughter, it can be either a string 
#     (i.e. terminal symbol) or another tree. 
#   - If there are multiple daughters, they must all be trees.

def make_tree(n, *daughters):
    assert len(daughters) > 0
    if len(daughters) == 1:
        assert type(daughters[0]) is str or is_valid(daughters[0])
        return (n, daughters[0])
    else:
        assert all(map(is_valid, daughters))
        return ((n,) + daughters)

def is_valid(e):
    if type(e) is tuple and len(e) >= 2 and type(e[0]) is str:
        if len(e) == 2:
            return (type(e[1]) is str) or is_valid(e[1])
        else:
            return all(map(is_valid, e[1:]))
    else:
        return False

def remove_trivial_unaries(e):
    assert type(e) is tuple
    assert len(e) >= 2
    if type(e[1]) is str:
        assert len(e) == 2
        return e
    else:
        new_daughters = [remove_trivial_unaries(x) for x in e[1:]]
        if len(new_daughters) == 1 and root_symbol(new_daughters[0]) == e[0]:
            return new_daughters[0]
        else:
            return make_tree(e[0], *new_daughters)

# Apply a function to all the leaves of a given tree
def map_leaves(f, e):
    if type(e) is str:
        return f(e)
    else:
        assert type(e) is tuple
        assert len(e) >= 2
        return make_tree(e[0], *[map_leaves(f,x) for x in e[1:]])

# Like map_leaves above, but the function f takes two 
# arguments, and POS tag and the leaf string; the return value 
# from the function f is the new leaf string.
def map_leaves_with_tag(f, e):
    assert type(e) is tuple
    assert len(e) >= 2
    if type(e[1]) is str:
        assert len(e) == 2
        return make_tree(e[0], f(e[0], e[1]))
    else:
        return make_tree(e[0], *[map_leaves_with_tag(f,x) for x in e[1:]])

# Apply a function to all the non-leaf node labels of a given tree
def map_nonleaf_labels(f, e):
    if type(e) is str:
        return e
    else:
        assert type(e) is tuple
        assert len(e) >= 2
        return make_tree(f(e[0]), *[map_nonleaf_labels(f,x) for x in e[1:]])

def replace_subtree(old, new, e):
    if e == old:
        return new
    else:
        if type(e) is str:
            return e
        else:
            assert type(e) is tuple
            assert len(e) >= 2
            return make_tree(e[0], *[replace_subtree(old, new, x) for x in e[1:]])

# List of words/leaves in a tree
def tree_yield(e):
    if type(e) is str:
        return [e]
    else:
        assert type(e) is tuple
        assert len(e) >= 2
        return reduce(lambda x,y: x+y , map(tree_yield,e[1:]))

# List of (POS,word) pairs in a tree
def tree_yield_with_tags(e):
    assert type(e) is tuple
    assert len(e) >= 2
    if type(e[1]) is str:
        assert len(e) == 2
        return [(e[0], e[1])]
    else:
        return reduce(lambda x,y: x+y , map(tree_yield_with_tags,e[1:]))

# List of all the (LHS,RHS) ``rewrites'', in leftmost-derivation order
def rewrites(e):
    assert type(e) is tuple
    assert len(e) >= 2
    if type(e[1]) is str:
        assert len(e) == 2
        return [(e[0], e[1])]
    else:
        this_rewrite = (e[0], tuple(map(root_symbol, e[1:])))
        return ([this_rewrite] + reduce(lambda x,y: x+y, map(rewrites,e[1:])))

def root_symbol(e):
    if type(e) is str:  # If it's a terminal string, just return that
        return e
    else:
        assert type(e) is tuple
        assert len(e) >= 2
        return e[0]

def to_string(e):
    if type(e) is str:
        return e
    else:
        assert type(e) is tuple
        assert len(e) >= 2
        component_strings = [str(e[0])] + [to_string(c) for c in e[1:]]
        return ("(" + " ".join(component_strings)  + ")")

###############################################################################

ROOT = "ROOT"

# Reads PTB trees from a file, and returns a list of trees
def get_trees(f):

    trees = []
    errors = 0
    for c in get_chunks(f):
        try:
            t = map_leaves(lambda x: x.lower(), parse_sexp(c))
            trees.append(t)
        except:
            errors = errors + 1
            print("WARNING: Ignoring ill-formed tree: %s" % re.sub("\s+", " ", c))

    if errors > 0:
        print("WARNING: Ignored %d ill-formed trees" % errors)

    return trees

def get_chunks(f):

    chunks = []
    current_chunk = None

    depth = 0
    c = f.read(1)
    while c != "":
        if c == "(":
            depth = depth + 1
            if depth == 1:
                # This is the opening paren for a top-level chunk
                assert current_chunk is None
                current_chunk = c
            else:
                # This is the opening paren for some internal chunk
                current_chunk = current_chunk + c
        elif c == ")":
            depth = depth - 1
            if depth == 0:
                # This is the closing paren for a top-level chunk
                current_chunk = current_chunk + c
                chunks.append(current_chunk)
                current_chunk = None
            else:
                # This is the closing paren for some internal chunk
                current_chunk = current_chunk + c
        else:
            if current_chunk is not None:
                current_chunk = current_chunk + c
        c = f.read(1)

    if (current_chunk is not None) or (depth != 0):
        print("WARNING: Treebank input ended with an incomplete parse tree")

    return chunks

# Parse a single s-expression, requiring either an unlabeled outer paren layer or a ROOT symbol
# e.g. parse_sexp("((S (NP John) (VP left)))")
# e.g. parse_sexp("(ROOT (S (NP John) (VP left)))")
def parse_sexp(s):

    with_spaces = re.sub(r'(\(|\))', " \\1 ", s)
    tokens = with_spaces.split()

    # If the trees come with an extra "unlabeled" pair of outer parentheses (like PTB), then 
    # we insert the label ROOT there.
    if tokens[:2] == ["(","("]:
        tokens[:2] = ["(",ROOT,"("]
    # Now, one way or the other, we should have a ROOT-labeled tree.
    assert tokens[:3] == ["(",ROOT,"("]

    # i is the ``current position'' in the buffer `tokens'
    def parse_worker(i):
        if tokens[i] == '(':
            i += 1
            result = []
            while tokens[i] != ')':
                (e, i) = parse_worker(i)
                result.append(e)
            return (make_tree(*result), i+1)
        else:
            return (tokens[i], i+1)

    (e, i) = parse_worker(0)
    assert i == len(tokens), ("Expected to get to the end of tokens; i = %d, len(tokens) = %d" % (i, len(tokens)))
    assert is_valid(e)
    return e
