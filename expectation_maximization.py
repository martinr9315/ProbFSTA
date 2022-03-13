from over_under import (get_address_list, get_context, get_node,
                        possible_lists, prob_over, prob_under)


class HiddenEvent:
    state = None  # this was mother state .. why?
    label = None
    children_states = []
    start = False

    def set_start(self, s):
        self.start = True
        self.state = s
    
    def set_transition(self, s, l, c):
        self.state = s
        self.label = l
        self.children_states = c

    def print(self):
        if self.start:
            print('HStart', self.state, end=' ')
        else:
            print('HStep', self.state, self.label, 
                  self.children_states, end=' ')


class SoftCounts:
    hidden_events = {}  # where hidden_events is dict of {HiddenEvent: Double}

    def __init__(self):
        self.hidden_events = {}
    
    def print(self):
        for k, v in self.hidden_events.items():
            k.print()
            print(':', v)


class ObservedEvents:
    start_event = None
    transition_events = []  # list of tuples of (node, node context)

    def __init__(self, node):
        self.start_event = node
        addresses = get_address_list(node)
        for a in addresses:
            self.transition_events.append((get_node(node, a), get_context(node, a)))

    def print(self):
        print('Start:', end=' ')
        self.start_event.print()
        print('\nTransitions:')
        for t in self.transition_events:
            t[0].print()
            print(": ", end='')
            t[1].print()
            print("\n")


def sum_counts(soft_counts_arr):
    summed_counts = SoftCounts()
    for counts in soft_counts_arr:
        for k, v in counts.hidden_events.items():
            summed_counts.hidden_events[k] = summed_counts.hidden_events.get(k, 0) + v
    return summed_counts


def normalize(d):  # not sure what this takes, hidden events? soft counts?
    values = d.values()
    total = sum(values)
    for k, v in d.items():
        d[k] = v/total
    return d

# -------------------E-step------------------


def expectations_from_observation(pfsta, observed_events):
    total_soft_counts = []
    # for start node:
    soft_start_counts = SoftCounts()
    for state in pfsta.q:
        h_event = HiddenEvent()
        h_event.set_start(state)
        soft_start_counts.hidden_events[h_event] = pfsta.start_prob(state) * prob_under(pfsta, observed_events.start_event, state)
    normalize(soft_start_counts.hidden_events)
    total_soft_counts.append(soft_start_counts)
    
    # for transitions:
    for t_event in observed_events.transition_events:
        t_soft_count = SoftCounts()
        node = t_event[0]
        context = t_event[1]
        k = len(node.children)
        if k == 0:
            # if has len 'after' == 0 aka no children 
            # then let likelihoods = M.fromList [(HStep q1 str q2, 
            # overValue m before q1 * trProb m (q1,q2) str * 
            # WHY DO I NEED THIS LINE: product(map (\(sbt, st) -> underValue m sbt st) (zip after q2)))  | q1 <- states, q2 <- [[]]] in 
        	# normalize likelihoods
            for q1 in pfsta.q:
                q2 = (())
                h_event = HiddenEvent()
                h_event.set_transition(q1, node.label, q2)
                prob = (prob_over(pfsta, context, q1)
                        * pfsta.transition_prob((q1, node.label, q2)))
                t_soft_count.hidden_events[h_event] = prob
            normalize(t_soft_count.hidden_events)
            total_soft_counts.append(t_soft_count)
        else:
            # let likelihoods = M.fromList [(HStep q1 str q2, 
            # overValue m before q1 * trProb m (q1,q2) str * 
            # product(map (\(sbt, st) -> underValue m sbt st) (zip after q2))) | q1 <- states, q2 <- possList k states] in 
        	# normalize likelihoods
            for q1 in pfsta.q:
                state_seq = possible_lists(pfsta, k)
                for q2 in state_seq:
                    h_event = HiddenEvent()
                    h_event.set_transition(q1, node.label, q2)
                    prob = (prob_over(pfsta, context, q1)
                            * pfsta.transition_prob((q1, node.label, q2)))
                    zipped = zip(node.children, q2)
                    for z in zipped:
                        prob *= prob_under(pfsta, z[0], z[1])
                    t_soft_count.hidden_events[h_event] = prob
            normalize(t_soft_count.hidden_events)
            total_soft_counts.append(t_soft_count)
    return total_soft_counts