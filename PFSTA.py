# PFSTA Python Implementation


class PFSTA:
    def __init__(self, q=[], i={}, delta={}):
        self.q = q          # q = [state]
        self.i = i          # i = {state:prob}
        self.delta = delta  # delta = {transition: prob}
        self.overs = {}
        self.unders = {}

    # ------ Grammar utilities ---------
    def all_states(self):
        return self.q

    def start_prob(self, state):
        return self.i.get(state, 0.0)

    def transition_prob(self, transition):
        return self.delta.get(transition, 0.0)

    def get_under(self, node, state):
        return self.unders.get((node, state))

    def get_over(self, context, state):
        return self.overs.get((context, state))

    def print(self):
        print('Q:', self.q)
        print('I:', self.i)
        print('Delta:', self.delta)

    def clean_print(self):
        print('Q:', self.q)
        print('I:', self.i)
        print('Delta:')
        for t, k in self.delta.items():
            if k > .00001:
                print(str(t)+':'+str(round(k, 4)))
    # ------------------------------------


class Node:
    def __init__(self, label="*"):
        self.children = []
        self.address = None
        self.label = label
        self.context = None

    def set_address(self, address):
        self.address = address

    def set_label(self, label):
        self.label = label

    def star_label(self):
        self.label = '*'

    def clear_tree_memos(self):
        self.under = {}
        self.under_no_order = {}
        if self.context:
            print('clear over')
            self.context.over = {}
            self.context.over_no_order = {}

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
