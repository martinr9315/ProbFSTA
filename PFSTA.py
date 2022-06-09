# PFSTA Python Implementation


class PFSTA:
    def __init__(self, q=[], i={}, delta={}):
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
        return self.delta.get(transition, 0.0)
 
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
    # -------------------------------------


class Node:
    def __init__(self, label="*"):
        self.children = []
        self.address = None
        self.label = label
        self.under = {}
        self.under_no_order = {}
        self.context = None

    def set_address(self, address):
        self.address = address
    
    def set_label(self, label):
        self.label = label

    def star_label(self):
        self.label = '*'

    def get_under(self, state):
        return self.under.get(state)
    
    def get_under_no_order(self, state):
        return self.under_no_order.get(state)

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
        self.over = {}
        self.over_no_order = {}

    def set_context(self, mother, mother_context, left_sisters, right_sisters):
        self.mother = mother
        self.mother_context = mother_context
        self.left_sisters = left_sisters
        self.right_sisters = right_sisters

    def set_root(self):
        self.root = True

    def is_root(self):
        return self.root

    def get_over(self, state):
        return self.over.get(state)

    def get_over_no_order(self, state):
        return self.over_no_order.get(state)

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
