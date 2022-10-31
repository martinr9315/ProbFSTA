from over_under import (get_address_list, get_context, get_node,
                        possible_lists, possible_lists_no_order, prob_over, prob_under,tree_prob_via_under_no_order,
                        prob_under_no_order, prob_over_no_order,
                        tree_prob_via_under, order, clear_memos)
from PFSTA import PFSTA
import math


class HiddenEvent:
    state = None
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

    def __eq__(self, other):
        if (self.state == other.state and
            self.label == other.label and
            self.children_states == other.children_states and
            self.start == other.start):
            return True
        return False

    def __hash__(self):
        return hash((self.state, self.label, tuple(self.children_states), self.start))

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

    def __init__(self):
        self.start_event = None
        self.transition_events = []
 
    def observe(self, node):
        self.start_event = node
        addresses = get_address_list(node)
        for a in addresses:
            self.transition_events.append((get_node(node, a),
                                           get_context(node, a)))

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


def normalize(d):
    values = d.values()
    if sum(values):
        total = sum(values)
    else:
        total = 1
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
        soft_start_counts.hidden_events[h_event] = (pfsta.start_prob(state) * prob_under(pfsta, observed_events.start_event, state))
    normalize(soft_start_counts.hidden_events)
    total_soft_counts.append(soft_start_counts)

    # for transitions:
    for t_event in observed_events.transition_events:
        t_soft_count = SoftCounts()
        node = t_event[0]
        context = t_event[1]
        k = len(node.children)
        for q1 in pfsta.q:
            state_seq = possible_lists(pfsta.q, k)
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


def expectations_from_observation_no_order(pfsta, observed_events):
    total_soft_counts = []
    # for start node:
    soft_start_counts = SoftCounts()
    for state in pfsta.q:
        h_event = HiddenEvent()
        h_event.set_start(state)
        soft_start_counts.hidden_events[h_event] = (pfsta.start_prob(state) * prob_under_no_order(pfsta, observed_events.start_event, state))
    normalize(soft_start_counts.hidden_events)
    total_soft_counts.append(soft_start_counts)

    # for transitions:
    for t_event in observed_events.transition_events:
        t_soft_count = SoftCounts()
        node = t_event[0]
        context = t_event[1]
        k = len(node.children)
        for q1 in pfsta.q:
            state_seq = possible_lists_no_order(pfsta.q, k)
            for q2 in state_seq:
                sum = 0
                if len(set(q2)) > 1:  # if the states are not same
                    ordered_list = order(q2, k)  # generate ordering 
                    h_event = HiddenEvent()
                    h_event.set_transition(q1, node.label, q2)
                    trans_prob = 0.0
                    for ordered_pair in ordered_list:
                        if pfsta.transition_prob((q1, node.label, ordered_pair)) != 0.0:
                            trans_prob = pfsta.transition_prob((q1, node.label, ordered_pair))
                            h_event.set_transition(q1, node.label, ordered_pair)
                            break
                    # if ordered, sum accross ordering
                    pair_sum = 0
                    for ordered_pair in ordered_list:
                        prob = prob_over_no_order(pfsta, context, q1) * trans_prob
                        zipped = zip(node.children, ordered_pair)
                        for z in zipped:
                            prob *= prob_under_no_order(pfsta, z[0], z[1])
                        pair_sum += prob
                    sum += pair_sum
                    t_soft_count.hidden_events[h_event] = sum
                else:
                    h_event = HiddenEvent()
                    h_event.set_transition(q1, node.label, q2)
                    # if (node.label == "C" and q1 == 1) or (node.label == "B" and q1 == 0):
                    #     h_event.print()
                    #     print(q1)
                    #     context.print()
                    prob = (prob_over_no_order(pfsta, context, q1)
                            * pfsta.transition_prob((q1, node.label, q2)))
                    zipped = zip(node.children, q2)
                    for z in zipped:
                        prob *= prob_under_no_order(pfsta, z[0], z[1])
                    t_soft_count.hidden_events[h_event] = prob
        normalize(t_soft_count.hidden_events)
        total_soft_counts.append(t_soft_count)
    return total_soft_counts


def expectations_from_corpus(pfsta, trees):
    all_soft_counts = []
    for t in trees:
        observed = ObservedEvents()
        observed.observe(t)
        all_soft_counts += expectations_from_observation(pfsta, observed)
    return sum_counts(all_soft_counts)


def expectations_from_corpus_no_order(pfsta, trees):
    all_soft_counts = []
    for t in trees:
        observed = ObservedEvents()
        observed.observe(t)
        all_soft_counts += expectations_from_observation_no_order(pfsta, observed)
    return sum_counts(all_soft_counts)


# -------------------M-step------------------


def estimate_from_counts(states, soft_counts):
    start_dist = {}
    step_dist = {}
    for hidden_event, prob in soft_counts.hidden_events.items():
        if hidden_event.start:
            start_dist[hidden_event.state] = prob
        else:
            dist_by_state = step_dist.get(hidden_event.state, {})
            dist_by_state[(hidden_event.state, hidden_event.label, 
                           hidden_event.children_states)] = prob
            step_dist[hidden_event.state] = dist_by_state
    flattened_step_dist = {}
    for dist in step_dist.values():
        normalize(dist)
        for k, v in dist.items():
            flattened_step_dist[k] = v
    normalize(start_dist)
    new_pfsta = PFSTA(states, start_dist, flattened_step_dist)
    return new_pfsta


def update(pfsta, trees):
    expected_counts = expectations_from_corpus(pfsta, trees)
    new_pfsta = estimate_from_counts(pfsta.q, expected_counts)
    pfsta.overs.clear()
    pfsta.unders.clear()
    return new_pfsta


def update_n(pfsta, trees, n):
    m = pfsta
    for _ in range(n):
        m = update(m, trees)
    return m


def update_no_order(pfsta, trees):
    expected_counts = expectations_from_corpus_no_order(pfsta, trees)
    new_pfsta = estimate_from_counts(pfsta.q, expected_counts)
    return new_pfsta


def update_no_order_n(pfsta, trees, n):
    m = pfsta
    for _ in range(n):
        m = update_no_order(m, trees)
    return m


def update_no_order_until(pfsta, trees, e):
    m = pfsta
    old_likelihood = 0
    new_likelihood = likelihood_no_order(pfsta, trees)
    while abs(old_likelihood-new_likelihood) > e:
        m = update_no_order_n(m, trees, 5)
        old_likelihood = new_likelihood
        new_likelihood = likelihood_no_order(m, trees)
        print(new_likelihood)
    return m


def likelihood(pfsta, trees):
    product = 1
    for t in trees:
        product *= tree_prob_via_under(pfsta, t)
    return product


def likelihood_no_order(pfsta, trees):
    product = 1
    for t in trees:
        prob = tree_prob_via_under_no_order(pfsta, t)
        if prob != 0:
            product += math.log(prob)
    return product
