from over_under import (get_address_list, get_context, get_node,
                        possible_lists, possible_lists_no_order, prob_over,
                        prob_under, tree_prob_via_under_no_order,
                        prob_under_no_order, prob_over_no_order,
                        tree_prob_via_under, order, make_pfsta, pfsta_values,
                        initialize_random)
from PFSTA import PFSTA
import numpy as np
import random, time
from scipy.optimize import minimize
from scipy.stats import entropy

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
    # print("  finished E step")
    new_pfsta = estimate_from_counts(pfsta.q, expected_counts)
    # print("  finished M step")
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
        m = update_no_order(m, trees)
        old_likelihood = new_likelihood
        new_likelihood = likelihood_no_order(m, trees)
        print('\tthis likelihood:', new_likelihood)
    return m


def likelihood(pfsta, trees):
    product = 1
    for t in trees:
        product *= tree_prob_via_under(pfsta, t)
    return product


def likelihood_no_order(pfsta, trees):
    product = 0
    for t in trees:
        prob = tree_prob_via_under_no_order(pfsta, t)
        if prob != 0:
            product += np.log(prob)
        if prob == 0:
            product += float('-inf')
    return product

######## with regularization


def likelihood_counts(pfsta, counts):
    sum = 0
    for hidden_event, count in counts.hidden_events.items():
        if hidden_event.start:
            prob = pfsta.start_prob(hidden_event.state)
            if prob:
                sum += count*np.log(prob)
        else:
            prob = pfsta.transition_prob((hidden_event.state, 
                                          hidden_event.label, 
                                          hidden_event.children_states))
            if prob:
                sum += count*np.log(prob)
            elif count !=0: 
                sum += -10000000 ## TODO: clean
    return sum


def L2_reward(pfsta):
    penalty = [0]*len(pfsta.q)
    for t, p in pfsta.delta.items():
        penalty[t[0]] += p**2
    return sum(penalty)

def entropy_penalty_1(pfsta):
    pk = np.array(pfsta_values(pfsta))
    H = entropy(pk)
    return H

def entropy_penalty(pfsta):
    entropy_by_state = [[] for _ in range(len(pfsta.q))]
    for t, prob in pfsta.delta.items():
        entropy_by_state[t[0]].append(prob)
    H = 0
    for q in entropy_by_state:
        H += entropy(np.array(q))
    return H

LAMBDA = 5

def obj(pfsta, counts):
    return -1*(likelihood_counts(pfsta, counts)+LAMBDA*L2_reward(pfsta))
    # return -1*(likelihood_counts(pfsta, counts)-entropy_penalty_1(pfsta))
    # return -1*(likelihood_counts(pfsta, counts)-LAMBDA*entropy_penalty(pfsta))


def maximize_from_counts_pen(soft_counts):
    objective_function = lambda v: obj(make_pfsta(v), soft_counts)
    p = PFSTA()
    initialize_random(p, 4, ['WH', 'V', 'X', 'NP'])
    guess = pfsta_values(p)
    st = time.time()
    result = minimize(objective_function, guess, method='Powell')
    et = time.time()
    print('\tmaximization time: %.2fs' % (et-st))
    optimized_x = result.x
    optimized_value = result.fun
    # print('opt',optimized_value)
    new_p = make_pfsta(result.x)
    # new_p.clean_print()
    return new_p

# squared soft threshold
THRESHOLD = .01

def squared_soft_threshold(d):
    scaled_d = {}
    for k, v in d.items():
        if v != 0:
            scaled_d[k] = np.power(v - THRESHOLD, 2)
    return scaled_d

def estimate_from_counts_sst(states, soft_counts):
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
        scaled = squared_soft_threshold(dist)
        normalize(scaled)
        for k, v in scaled.items():
            flattened_step_dist[k] = v
    normalize(start_dist)
    new_pfsta = PFSTA(states, start_dist, flattened_step_dist)
    return new_pfsta

def update_sst(pfsta, trees):
    expected_counts = expectations_from_corpus_no_order(pfsta, trees)
    new_pfsta = estimate_from_counts_sst(pfsta.q, expected_counts)
    pfsta.overs.clear()
    pfsta.unders.clear()
    return new_pfsta

def update_no_order_until_sst(pfsta, trees, e):
    m = pfsta
    old_likelihood = 0
    new_likelihood = likelihood_no_order_sst(pfsta, trees)
    while abs(old_likelihood-new_likelihood) > e:
        m = update_sst(m, trees)
        old_likelihood = new_likelihood
        new_likelihood = likelihood_no_order_sst(m, trees)
        print('\tsst likelihood:', new_likelihood)
    return m

def likelihood_no_order_sst(pfsta, trees):
    product = 0
    for t in trees:
        prob = tree_prob_via_under_no_order(pfsta, t)
        if prob != 0:
            product += np.log(prob)
        if prob == 0:
            product += float('-inf')
    penalty = 0
    # for k,v in pfsta.delta.items():
    #     if v!=0:
    #         penalty += np.power(np.maximum(v - THRESHOLD, 0.0000001), 2)
    return product - penalty

# penalization
def update_pen(pfsta, trees):
    expected_counts = expectations_from_corpus_no_order(pfsta, trees)
    # new_pfsta = estimate_from_counts(pfsta.q, expected_counts)
    new_pfsta = maximize_from_counts_pen(expected_counts)
    reward = L2_reward(pfsta)
    # penalty = entropy_penalty_1(pfsta)
    # penalty = entropy_penalty(pfsta)
    obj = likelihood_no_order(new_pfsta, trees)+reward
    # obj = likelihood_no_order(new_pfsta, trees)-penalty
    print('o:', obj, '\t\tl:',likelihood_no_order(new_pfsta, trees))
    print('\treward:', reward )
    # print('\tpenalty (2):', penalty )
    pfsta.overs.clear()
    pfsta.unders.clear()
    return new_pfsta, obj

def update_no_order_until_pen(pfsta, trees, e):
    print('lambda:', LAMBDA)
    m = pfsta
    old_likelihood = 1
    new_likelihood = 0
    while abs(old_likelihood-new_likelihood) > e:
        old_likelihood = new_likelihood
        m, new_likelihood = update_pen(m, trees)
        # print('\tlikelihood:', new_likelihood)
    return m, new_likelihood