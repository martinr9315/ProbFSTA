# PFSTA Python Implementation

# Comments: made assumption that trees are binary

# root: empty string not zero
# root of subtrees is not 0 address
# make trees n-ary
# break trees into over and two under
# read from text files


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
        self.i.get(state, 0.0)

    def transition_prob(self, transition):
        self.delta.get(transition, 0.0)
    # -------------------------------------


class Node:
    def __init__(self, label="*"):
        self.left = None
        self.right = None
        self.address = None
        self.label = label

    def set_address(self, address):
        self.address = address

    def print(self):
        print("Node "+self.label, end=' ')

    def print_addresses(self):
        print(self.address+":"+self.label)


class TreeContext:
    def __init__(self):
        self.mother = None
        self.mother_context = None
        self.left_sisters = None
        self.right_sisters = None
        self.root = False

    def set_context(self, mother, mother_context, left_sisters, right_sisters):
        self.mother = mother
        self.mother_context = mother_context
        self.left_sisters = left_sisters
        self.right_sisters = right_sisters

    def set_root(self):
        self.root = True

    def print(self):
        print("[", end=' ')
        if self.root is True:
            print("Root", end=' ')
        else:
            to_print = [self.mother, self.mother_context, self.left_sisters,
                        self.right_sisters]
            for obj in to_print:
                if obj:
                    obj.print()
                else:
                    print(None, end=' ')
        print("]", end=' ')

#  ----------- Tree utilities -------------
# nthsubt - not necessary in Python


def assign_addresses(node):
    if node.left:
        node.left.set_address(node.address+'0')
        assign_addresses(node.left)
    if node.right:
        node.right.set_address(node.address+'1')
        assign_addresses(node.right)


def get_label(root, address):  # getLabel
    node = root
    for num in address[1:]:
        if num == '0':
            node = node.left
        elif num == '1':
            node = node.right
    return (node.label)


def get_node(root, address):  # getSubTree
    node = root
    for num in address[1:]:
        if num == '0':
            node = node.left
        elif num == '1':
            node = node.right
    return (node)


def get_left_sis(root, address):  # getLeftSis
    if address == '0':
        return None
    elif address[-1] == '0':
        return None
    else:
        return(get_node(root, address[:-1]+'0'))


def get_right_sis(root, address):  # getRightSis
    if address == '0':
        return None
    elif address[-1] == '1':
        return None
    else:
        return(get_node(root, address[:-1]+'1'))


def get_context(root, address):  # getCxt
    if address == '0':
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
        node.print_addresses()
        print_tree(node.left)
        print_tree(node.right)

# -----------------------------------------------


root = Node('a')
root.set_address('0')
root.left = Node('b')
root.right = Node('c')
root.right.left = Node('d')
root.right.right = Node('e')

assign_addresses(root)

print_tree(root)

# print(get_label(root, '011'))
# get_right_sis(root, '010').print()
# print(get_left_sis(root, '00'))

# get_context(root, '00').print()
get_context(root, '010').print()


