from trees import get_trees
from PFSTA import Node
from over_under import (assign_addresses, print_tree, get_right_sis, get_left_sis, get_address_list, 
                        get_node, star_nodes,get_terminals, depth)
import signal, string, re

VERB_LABELS = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'COP']

def raw(t):
    return ''.join(ch for ch in str(t) if not ch.isupper() 
                                          and ch not in string.punctuation 
                                          and not ch.isnumeric())


def from_tuple(t):
    if not isinstance(t, tuple):
        return Node(t)
    if len(t) > 0:
        return Node(t[0], children=[from_tuple(x) for x in t[1:]])


def remove_animacy(tuple_of_strings):
    # ensure that the input argument is a tuple
    if not isinstance(tuple_of_strings, tuple):
        raise TypeError("Input argument must be a tuple of strings")

    cleaned_strings = []
    for text in tuple_of_strings:
        # if the current item is a tuple, recurse into the tuple
        if isinstance(text, tuple):
            cleaned_strings.append(remove_animacy(text))
        # ensure that each item in the tuple is a string
        elif not isinstance(text, str):
            raise TypeError("Items in the tuple must be strings")
        else:
            # use regex to find and remove anything in angle brackets
            cleaned_text = re.sub(r'<[^>]*>', '', text)
            cleaned_strings.append(cleaned_text)

    return tuple(cleaned_strings)


def remove_trailing_hyphen(t):
    if not isinstance(t, tuple):
        raise TypeError("Input argument must be a tuple")

    result = []
    for item in t:
        if isinstance(item, str):
            # remove trailing hyphens from the string
            cleaned_string = item.rstrip('-')
            result.append(cleaned_string)
        elif isinstance(item, tuple):
            # recursively call remove_trailing_hyphen on the nested tuple
            nested_result = remove_trailing_hyphen(item)
            result.append(nested_result)
        else:
            raise TypeError("Tuple must contain only strings or tuples")
    return tuple(result)


def drop_punctuation(node): 
    if not node.children:
        return
    node.children = [child for child in node.children if child.label not in string.punctuation]
    for child in node.children:
        drop_punctuation(child)


def drop_traces(node): 
    if not node.children:
        return
    node.children = [child for child in node.children if child.label !='trace']
    for child in node.children:
        drop_traces(child)


def collapse_unary(node):
    if not node.children:
        return node
    if node.label in ['V', 'NP', 'WH', 'trace']:
        node.children = []
    elif len(node.children) == 1:
        return collapse_unary(node.children[0])
    else:
        for i, child in enumerate(node.children):
            node.children[i] = collapse_unary(child)
    return node


def binarize(node):
    if not node.children:
        return node
    left = node.children[0]
    right = node.children[1:]
    if len(node.children) == 1:
        return Node(label=node.label, children=[binarize(left)])
    elif len(node.children) == 2:
        return Node(label=node.label, children=[binarize(left), binarize(right[0])])
    elif len(node.children) > 2:
        # make V and NP children of one new node if they have sisters other than each other
        updated_children = []
        for i, c in enumerate(node.children): 
            if c.get_label() == 'NP' or c.get_label() == 'trace':
                new_node = Node(children=[node.children[i-1], c])
                updated_children.pop()
                updated_children.append(new_node)
            else:
                updated_children.append(c)
        left = updated_children[0]
        right = updated_children[1:]
        if len(updated_children) > 2:
            return Node(label=node.label, children=[binarize(left), binarize(Node(children=right))])
        else:
            return Node(label=node.label, children=[binarize(left), binarize(right[0])])


def timeout_handler(signum, frame):
    raise TimeoutError("Computation timed out.")


def test_binarize():
    tree1 = Node('*')
    tree1.children = [Node('V'), Node('NP'), Node('X')]
    tree1.set_address('')
    assign_addresses(tree1)
    print_tree(tree1)
    print('binarize')
    binary_tree = binarize(tree1)
    binary_tree.set_address('')
    assign_addresses(binary_tree)
    print_tree(binary_tree)


def test_collapse():
    tree1 = Node('*')
    tree1.children = [Node('*')]
    tree1.children[0].children = [Node('V'), Node('NP'), Node('X'), Node('V'), Node('NP')]
    tree1.set_address('')
    assign_addresses(tree1)
    print_tree(tree1)
    print('collapse')
    collapsed = collapse_unary(tree1)
    collapsed.set_address('')
    assign_addresses(collapsed)
    print_tree(collapsed)


def split_bank(bank):
    wh = []
    v_np = []
    c_only = []
    for t in bank:
        if 'WH' in get_terminals(t):
            wh.append(t)
        elif 'NP' in get_terminals(t):
            v_np.append(t)
        else:
            c_only.append(t)
    split_bank = {'wh': wh, 'v_np': v_np, 'c_only': c_only}
    return split_bank


def depth_limit(bank, n):
    shallow_bank = []
    for t in bank:
        if len(depth(t)) < n:
            shallow_bank.append(t)
    return shallow_bank


def undo_copular_inversion(root):
    root.set_address('')
    assign_addresses(root)
    addresses = get_address_list(root)
    for a in addresses:
        n = get_node(root, a)
        if n.get_label() == 'SQ':
            sq_node = n
            if sq_node.children[0].get_label() == 'VP':
                vp_node = sq_node.children[0]
                if len(vp_node.children) > 2 and vp_node.children[0].get_label() == 'COP':
                    cop_node = vp_node.children[0]
                    right_sis = get_right_sis(root, cop_node.get_address())
                    if len(right_sis) == 2 and right_sis[0].label == 'NP' and right_sis[1].label == 'NP':
                        sq_node.children.insert(0, right_sis[0])
                        del vp_node.children[1]
                        root.set_address('')
                        assign_addresses(root)
                        return


def clean_labels(root):
    root.set_address('')
    assign_addresses(root)
    addresses = get_address_list(root)
    traces = []
    for a in addresses:
        n = get_node(root, a)
        if n.get_label() in VERB_LABELS or n.get_label() == 'PP': # to include PP structure (a), add 'PP' to this list
            n.set_label('V')
            right_sis = get_right_sis(root, a)
            if len(right_sis) == 0 or right_sis[0].label != 'NP':
                n.set_label('X')
        elif n.get_label() == 'NP':
            left_sis = get_left_sis(root, a)
            if len(left_sis) == 0 or left_sis[len(left_sis)-1].label != 'V':
                n.set_label('X')
            else:
                for c in n.children:
                    if '-NONE-ABAR-' in c.label:
                        traces.append(c.children[0].label[-1])
                        n.set_label('trace')
        elif n.get_label() not in string.punctuation and 'WHNP' not in n.get_label() and 'PP' not in n.get_label():
            n.set_label('X')
    for a in addresses:
        n = get_node(root, a)
        if 'WHNP' in n.get_label() and n.get_label()[-1] in traces:
            n.set_label('WH')
    for a in addresses:
        n = get_node(root, a)
        if 'PP' in n.get_label():
            n.set_label('X')


def parse(filenames):
    bank = []
    wh_trees = 0
    whnp_trees = 0
    whnp_tr_trees = 0
    whnp_obj_trees = 0
    count = 0
    for filename in filenames:
        f = open(filename, "r")
        trees = get_trees(f)
        for i, t in enumerate(trees):
            t = remove_trailing_hyphen(remove_animacy(t))
            original = t
            tuple_tree = from_tuple(t)              # convert from tuple to tree
            undo_copular_inversion(tuple_tree)
            clean_labels(tuple_tree)    # rewrite V w/o NP sister as C, only WHs with traces
            drop_punctuation(tuple_tree)            # drop punctuation
            tree = collapse_unary(tuple_tree)       # collapse unary branches (w/ same label) and complex V,NP
            star_nodes(tree)                        # star all inner nodes
            tree = binarize(tree)                   # binarize tree
            drop_traces(tree)                       # drop traces
            tree.set_address('')                    # set addresses
            assign_addresses(tree)
            if i not in [1801, 16194, 28312, 6564] and 'kind' not in str(original):
                bank.append(tree)
            if 'WHNP' in str(original):
                whnp_trees += 1
                if '-NONE-ABAR-' in str(original): 
                    whnp_tr_trees += 1
                    if "('SQ', ('NP', ('-NONE-ABAR-WH', '*t*-1')), ('VP'" not in str(original):
                        whnp_obj_trees += 1
                        # if any(v in str(original) for v in VERB_LABELS): 
                        #     COP_pattern = r"'COP', (?:'is'|'are'|'were'|'was'|\"'s\")\), \('NP', \('-NONE-ABAR-WH-'"
                        #     if not re.search(COP_pattern, str(original)):
                        #         whnp_tr_obj_lex_trees += 1
                        # with open("whnp-diff-full.txt", "a") as f:
                        #     if 'WH' not in get_terminals(tree):
                        #             print(i, raw(original), '\n', file=f)
                        #             print(i, original, '\n', file=f)
                                # print(original)
                                # print_tree(tree)
            if 'WH' in get_terminals(tree):
                wh_trees += 1
            count += 1

    # print('\n# trees:', count)
    # print('WHNP trees:', whnp_trees, '-->', '{:.2%}'.format(whnp_trees/count)) 
    # print('\twith trace:', whnp_tr_trees, '-->', '{:.2%}'.format(whnp_tr_trees/count))
    # print('\t\twithout subject question:', whnp_obj_trees, '-->', '{:.2%}'.format(whnp_obj_trees/count))

    # print('WH trees:', wh_trees, '-->', '{:.2%}'.format(wh_trees/count))
    # print('original contains WHNP -> parsed contains no WH:', whnp_obj_trees-wh_trees)

    return bank
