# PFSTA Python Implementation
import itertools

# TODO:
# finish prob_over
# memoize -- states to under values


class PFSTA:
    def __init__(self, q, i, delta):
        self.q = q          # q = [state]
        self.i = i          # i = {state:prob}
        self.delta = delta  # delta = {transition: prob}
        #                     where transition is a tuple of form:
        #                     (state, node_label, [states])

    # ------ Grammar utilities ----------
    def all_states(self):
        return self.q

    def start_prob(self, state):
        return self.i.get(state, 0.0)

    def transition_prob(self, transition):
        # if self.delta.get(transition):
        #     print(self.delta.get(transition))
        return self.delta.get(transition, 0.0)
    # -------------------------------------


class Node:
    def __init__(self, label="*"):
        self.children = []
        self.address = None
        self.label = label
        self.over = None
        self.under = None

    def set_address(self, address):
        self.address = address

    def star_label(self):
        self.label = '*'

    def print(self):
        print("Node "+self.label, end=' ')

    def print_address(self):
        print(self.address+":"+self.label)


class TreeContext:
    def __init__(self):
        self.mother = None
        self.mother_context = None
        self.left_sisters = []
        self.right_sisters = []
        self.root = False
        self.over = None

    def set_context(self, mother, mother_context, left_sisters, right_sisters):
        self.mother = mother
        self.mother_context = mother_context
        self.left_sisters = left_sisters
        self.right_sisters = right_sisters

    def set_root(self):
        self.root = True
    
    def is_root(self):
        return self.root

    def print(self):
        print("[", end=' ')
        if self.root is True:
            print("Root", end=' ')
        else:
            to_print = [self.mother, self.mother_context, self.left_sisters,
                        self.right_sisters]
            for obj in to_print:
                if type(obj) == list:
                    print("(", end=' ')
                    for s in obj:
                        s.print()
                    print(")", end=' ')
                elif obj:
                    obj.print()
                else:
                    print(None, end=' ')
        print("]", end=' ')

#  ----------- Tree utilities -------------
# nthsubt - not necessary in Python


def assign_addresses(node):
    for i, n in enumerate(node.children):
        if n:
            n.set_address(node.address+str(i))
            assign_addresses(n)


def get_label(root, address):  # getLabel
    node = root
    for num in address[1:]:
        node = node.children[int(num)]
    return (node.label)


def get_node(root, address):  # getSubTree
    node = root
    for num in address:
        node = node.children[int(num)]
    return (node)


def get_left_sis(root, address):  # getLeftSis
    if address == '':
        return None
    else:
        mother = get_node(root, address[:-1])
        left_sisters = []
        for n in mother.children:
            if n and (n.address < address):
                left_sisters.append(n)
        return left_sisters


def get_right_sis(root, address):  # getRightSis
    if address == '':
        return None
    else:
        mother = get_node(root, address[:-1])
        right_sisters = []
        for n in mother.children:
            if n and (n.address > address):
                right_sisters.append(n)
        return right_sisters


def get_context(root, address):  # getCxt
    if address == '':
        root_context = TreeContext()
        root_context.set_root()
        return root_context
    mother = get_node(root, address[:-1])
    left_sisters = get_left_sis(root, address)
    right_sisters = get_right_sis(root, address)
    mother_context = get_context(root, address[:-1])
    context = TreeContext()
    context.set_context(mother, mother_context, left_sisters, right_sisters)
    return context


def print_tree(node):  # getAdsList
    if node:
        node.print_address()
        for i, n in enumerate(node.children):
            print_tree(n)

# -------------- Over/Under Utilities ---------------------------


def possible_lists(pfsta, n):
    return set(list(itertools.permutations(pfsta.q, n)) +
               list(itertools.combinations_with_replacement(pfsta.q, n)))


def zip_three(s1, s2, s3):
    zipped = []
    for i1 in s1:
        for i2 in s2:
            for i3 in s3:
                zipped.append((i1, i2, i3))
    return zipped


def filter_through(stset, para):
    possible_states = list(itertools.permutations(stset))
    matches = []
    for s in possible_states:
        if s == para:
            matches.append(s)
    return matches

# ------------ Reading trees ------------------------


def read_trees(file):
    trees = []
    with open(file) as f:
        lines = f.read()
        lines = lines.split('\n\n\n')
        for l in lines:
            s = clean(l)
            string = split_into_nodes(s)
            root = tree_from_string(string, 0, len(string)-1)
            root.set_address('')
            assign_addresses(root)
            trees.append(root)
    return trees


def clean(s):
    to_remove = [" ", "\n", "(.?)", "(..)"]
    s = s[1:-1]
    for r in to_remove:
        s = s.replace(r, "")
    return s


def split_into_nodes(s):
    tree = []
    i = 0
    while i < len(s):
        label = ""
        if s[i] == ')' or s[i] == '(':
            tree.append(s[i])
            i += 1
        else:
            j = i
            while j < len(s) and s[j] != ')' and s[j] != '(':
                label += s[j]
                j += 1
            i = j
            tree.append(label)
    return tree


def find_index(s, si, ei):
    if (si > ei):
        return -1
    stack = []
    for i in range(si, ei + 1):
        if (s[i] == '('):
            stack.append(s[i])
        elif (s[i] == ')'):
            if (stack[-1] == '('):
                stack.pop(-1)
                if len(stack) == 0:
                    return i
    return -1


def tree_from_string(s, si, ei):
    if (si > ei):
        return None
    root = Node(s[si])
    index = -1
    if (si + 1 <= ei and s[si + 1] == '('):
        index = find_index(s, si + 1, ei)
    if (index != -1):
        root.children = [tree_from_string(s, si + 2, index-1),
                         tree_from_string(s, index + 2, ei-1)]
    return root


def star_nodes(node):
    if node and node.children:
        node.star_label()
        for i, n in enumerate(node.children):
            star_nodes(n)


# ---------------------recursive under------------------------

def prob_under(pfsta, node, state):
    if node.under:
        return node.under
    else:
        if not node.children:
            return pfsta.transition_prob((state, node.label, ()))
        else:
            k = len(node.children)
            state_seq = possible_lists(pfsta, k)
            sum = 0
            for st in state_seq:
                zipped = list(zip(node.children, st))
                product = pfsta.transition_prob((state, node.label, st))
                for z in zipped:
                    product *= prob_under(pfsta, z[0], z[1])
                sum += product
            node.under = sum
            return sum


# probOver:: ProbFSTA -> TreeCxt -> State -> Double
# --base case: we are at the root of the tree, just find the initial parameter I(st)
# probOver pfsa Root st = startProb pfsa st
# --recursive step: we are interested P(this tree context is at state st)
# --str:: NodeLabel; mother node label
# --cxt:: TreeCxt; mother node conext
# --lsubt:: [Tree]; left sisters
# --rsubt:: [Tree]; right sisters 
# probOver pfsa (Nonroot str cxt lsubt rsubt) st = let stateList = allStates pfsa in
# 	let kl = length lsubt in --get # of left sisters
#             let kr = length rsubt in -- get # of right sisters
#             sum(map (\(lstateSeq, rstateSeq, momState) -> (probOver pfsa cxt momState)* --OverValue P(mother node context is in state momState)
#             	                                           product(map (\(sbt, state) -> (probUnder pfsa sbt state)) (zip lsubt lstateSeq)) *  --big products over all UnderValues P(sbt is in state)
#             	                                           product(map (\(rsbt, rstate) -> (probUnder pfsa rsbt rstate)) (zip rsubt rstateSeq)) * --big products over all UnderValues P(rsbt is in rstate)
#             	                                           trProb pfsa (momState, concat [lstateSeq, [st], rstateSeq]) str) --get the transition probability: (momState, str, [lStateSeq]+[st]+[rStateSeq])
#                 (zipthree (possList kl stateList) (possList kr stateList) (stateList)))
# --lstateSeq: [States]; each slot corresponds to the state of each left sister
# --rstateSeq: [States]; each slot corresponds to the state of each right sister
# --momState: the possible state that the mother node is in
# --Big sum scoping over the combinations of all three possible lists (thus, zipping them together)


def prob_over(pfsta, context, state):
    if context.over:
        return context.over
    else:
        if context.is_root():
            return pfsta.start_prob(state)
        else:
            mother_label = context.mother.label
            kl = len(context.left_sisters)
            kr = len(context.right_sisters)
            poss_list_left = possible_lists(pfsta, kl)
            poss_list_right = possible_lists(pfsta, kr)
            zipped = zip_three(poss_list_left, poss_list_right, pfsta.q)
            sum = 0
            final_product = 0
            for l_state_seq, r_state_seq, mom_state in zipped:
                product = pfsta.transition_prob((mom_state, mother_label, (l_state_seq+(state,)+r_state_seq)))
                if product:
                    product *= prob_over(pfsta, context.mother_context, mom_state)
                    left_under = 1
                    for i, l_sis in enumerate(context.left_sisters):
                        left_under *= prob_under(pfsta, l_sis, l_state_seq[i])
                    right_under = 1
                    for i, r_sis in enumerate(context.right_sisters):
                        right_under *= prob_under(pfsta, r_sis, r_state_seq[i])
                    product *= left_under * right_under
                    final_product = product
            sum += final_product
            context.over = sum
            return sum
            
# -----------------------------------------------


root1 = Node('a')
root1.set_address('')
root1.children = [Node('b'), Node('c')]
root1.children[1].children = [Node('d'), Node('e')]
assign_addresses(root1)
# print_tree(root1)
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

# print(prob_under(pfsta1, root1, 1))
print(prob_over(pfsta1, get_context(root1, "0"), 2))
