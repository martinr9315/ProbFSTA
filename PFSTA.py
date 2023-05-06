# PFSTA Python Implementation


class PFSTA:
    def __init__(self, q=[], i={}, delta={}):
        self.q = q          # q = [state]
        self.i = i          # i = {state:prob}
        self.delta = delta  # delta = {transition: prob}
        self.overs = {}
        self.unders = {}
        self.order_transitions()  # only for unordered PFSTAs

    # ------ Grammar utilities ---------
    def all_states(self):
        return self.q

    def start_prob(self, state):
        return self.i.get(state, 0.0)

    def transition_prob(self, transition):
        return self.delta.get(transition, 0.0)

    def order_transitions(self):
        ordered_delta = {}
        for t, v in self.delta.items():
            if len(t[2]) > 0:
                sorted_children = tuple(sorted(t[2]))
                sorted_transition = (t[0], t[1], sorted_children)
                t = sorted_transition
            ordered_delta.update({t: v})
        self.delta = ordered_delta

############
    def possible_transitions(self, state):
        return {t: self.transition_prob(t) for t in self.delta if t[0] == state}

    def get_terminals(self):
        return [t[1] for t in self.delta if len(t[2]) == 0]
    
    def get_state(self, output):
        for t in self.delta.keys():
            if output[0] == t[1] and output[1] == t[2]:
                return t[0]
        
############

    def get_under(self, node, state):
        return self.unders.get((node, state))

    def get_over(self, context, state):
        return self.overs.get((context, state))

    def print(self):
        print('Q:', self.q)
        print('I:', self.i)
        print('Delta:')
        for t, k in self.delta.items():
                print(str(t)+': '+str(round(k, 4)))

    def clean_print(self):
        print('Q:', self.q)
        cleaned_i = {t: k for t, k in self.i.items() if k > .00001}
        print('I:', cleaned_i)
        print('Delta:')
        for t, k in self.delta.items():
            if k > .00001:
                print(str(t)+': '+str(round(k, 4)))

    def pretty_print(self, assignment):
        for i, k in self.i.items():
            if k > .00001:
                print('I:', assignment.get(i, '*'))
        for t, k in self.delta.items():
            if k > .00001:
                if len(t[2]) == 1:
                    print(assignment.get(t[0], '*'),
                          "->",
                          assignment.get(t[2][0], '*'))
                elif len(t[2]) == 2:
                    print(assignment.get(t[0], '*'),
                          "->",
                          assignment.get(t[2][0], '*'),
                          assignment.get(t[2][1], '*'))
                else:
                    print(assignment.get(t[0], '*'),
                          "->", t[1])
    # ------------------------------------


class Node:
    def __init__(self, label="*", children=[]):
        self.children = children
        self.address = None
        self.label = label
        self.context = None
        self.state = None  # only for use in annotated trees

    def set_address(self, address):
        self.address = address

    def get_address(self):
        return self.address

    def set_label(self, label):
        self.label = label
    
    def get_label(self):
        return self.label

    def star_label(self):
        self.label = '*'
    
    def set_state(self, state):
        self.state = state
    
    def get_state(self):
        return self.state

    def clear_tree_memos(self):
        self.under = {}
        self.under_no_order = {}
        if self.context:
            self.context.over = {}
            self.context.over_no_order = {}

    def print(self):
        print("Node "+self.label, end=' ')

    def annotated_print(self):
        print(self.address+":"+str(self.state)+', '+self.label)

    def print_address(self, f=None):
        if f is not None:
            print(self.address+":"+self.label, file=f)
        print(self.address+":"+self.label)
        # return (self.address+":"+self.label)


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
