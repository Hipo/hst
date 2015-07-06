"""
from: http://blog.notdot.net/2010/07/Damn-Cool-Algorithms-Levenshtein-Automata
"""
import bisect

class NFA(object):
  EPSILON = object()
  ANY = object()
  
  def __init__(self, start_state):
    self.transitions = {}
    self.final_states = set()
    self._start_state = start_state
  
  @property
  def start_state(self):
    return frozenset(self._expand(set([self._start_state])))
  
  def add_transition(self, src, input, dest):
    self.transitions.setdefault(src, {}).setdefault(input, set()).add(dest)

  def add_final_state(self, state):
    self.final_states.add(state)
  
  def is_final(self, states):
    return self.final_states.intersection(states)
  
  def _expand(self, states):
    frontier = set(states)
    while frontier:
      state = frontier.pop()
      new_states = self.transitions.get(state, {}).get(NFA.EPSILON, set()).difference(states)
      frontier.update(new_states)
      states.update(new_states)
    return states
  
  def next_state(self, states, input):
    dest_states = set()
    for state in states:
      state_transitions = self.transitions.get(state, {})
      dest_states.update(state_transitions.get(input, []))
      dest_states.update(state_transitions.get(NFA.ANY, []))
    return frozenset(self._expand(dest_states))
  
  def get_inputs(self, states):
    inputs = set()
    for state in states:
      inputs.update(self.transitions.get(state, {}).keys())
    return inputs
  
  def to_dfa(self):
    dfa = DFA(self.start_state)
    frontier = [self.start_state]
    seen = set()
    while frontier:
      current = frontier.pop()
      inputs = self.get_inputs(current)
      for input in inputs:
        if input == NFA.EPSILON: continue
        new_state = self.next_state(current, input)
        if new_state not in seen:
          frontier.append(new_state)
          seen.add(new_state)
          if self.is_final(new_state):
            dfa.add_final_state(new_state)
        if input == NFA.ANY:
          dfa.set_default_transition(current, new_state)
        else:
          dfa.add_transition(current, input, new_state)
    return dfa


class DFA(object):
  def __init__(self, start_state):
    self.start_state = start_state
    self.transitions = {}
    self.defaults = {}
    self.final_states = set()
  
  def add_transition(self, src, input, dest):
    self.transitions.setdefault(src, {})[input] = dest
  
  def set_default_transition(self, src, dest):
    self.defaults[src] = dest
  
  def add_final_state(self, state):
    self.final_states.add(state)

  def is_final(self, state):
    return state in self.final_states
  
  def next_state(self, src, input):
    state_transitions = self.transitions.get(src, {})
    return state_transitions.get(input, self.defaults.get(src, None))

  def next_valid_string(self, input):
    state = self.start_state
    stack = []
    
    # Evaluate the DFA as far as possible
    for i, x in enumerate(input):
      stack.append((input[:i], state, x))
      state = self.next_state(state, x)
      if not state: break
    else:
      stack.append((input[:i+1], state, None))

    if self.is_final(state):
      # Input word is already valid
      return input
    
    # Perform a 'wall following' search for the lexicographically smallest
    # accepting state.
    while stack:
      path, state, x = stack.pop()
      x = self.find_next_edge(state, x)
      if x:
        path += x
        state = self.next_state(state, x)
        if self.is_final(state):
          return path
        stack.append((path, state, None))
    return None

  def find_next_edge(self, s, x):
    if x is None:
      x = u'\0'
    else:
      x = unichr(ord(x) + 1)
    state_transitions = self.transitions.get(s, {})
    if x in state_transitions or s in self.defaults:
      return x
    labels = sorted(state_transitions.keys())
    pos = bisect.bisect_left(labels, x)
    if pos < len(labels):
      return labels[pos]
    return None
    

def levenshtein_automata(term, k):
  nfa = NFA((0, 0))
  for i, c in enumerate(term):
    for e in range(k + 1):
      # Correct character
      nfa.add_transition((i, e), c, (i + 1, e))
      if e < k:
        # Deletion
        nfa.add_transition((i, e), NFA.ANY, (i, e + 1))
        # Insertion
        nfa.add_transition((i, e), NFA.EPSILON, (i + 1, e + 1))
        # Substitution
        nfa.add_transition((i, e), NFA.ANY, (i + 1, e + 1))
  for e in range(k + 1):
    if e < k:
      nfa.add_transition((len(term), e), NFA.ANY, (len(term), e + 1))
    nfa.add_final_state((len(term), e))
  return nfa


def find_all_matches(word, k, lookup_func):
  """Uses lookup_func to find all words within levenshtein distance k of word.
  
  Args:
    word: The word to look up
    k: Maximum edit distance
    lookup_func: A single argument function that returns the first word in the
      database that is greater than or equal to the input argument.
  Yields:
    Every matching word within levenshtein distance k from the database.
  """
  lev = levenshtein_automata(word, k).to_dfa()
  match = lev.next_valid_string(u'\0')
  while match:
    next = lookup_func(match)
    if not next:
      return
    if match == next:
      yield match
      next = next + u'\0'
    match = lev.next_valid_string(next)

class Matcher(object):
  def __init__(self, l):
    self.l = l
    self.probes = 0

  def __call__(self, w):
    self.probes += 1
    pos = bisect.bisect_left(self.l, w)
    if pos < len(self.l):
      return self.l[pos]
    else:
      return None

import re
r = re.compile("[a-zA-Z0-9]+")

def tokenize(s):
    l = r.findall(s)
    return l

if __name__ == '__main__':
    print tokenize("ssh -i app1.moment.com -- echo 'hello world'")
    words = set()
    for line in open('history.txt').readlines():
        s = line.strip().lower().decode('utf-8')
        ws = tokenize(s)
        for w in ws:
            words.add(w)
    words = list(words)
    words.sort()
    print len(words)

    m = Matcher(words)
    import time
    t1 = time.time()
    print list(find_all_matches('momnt', 2, m))
    print ">>", time.time() - t1
    t1 = time.time()
    print list(find_all_matches('ssh', 1, m))
    print ">>", time.time() - t1