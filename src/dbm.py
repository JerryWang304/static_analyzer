######################################
#
# dbms.py 
#
# Difference bound matrices ADT
#
# (C) 2016, Andreas Gaiser
######################################

import numbers
import abc
import copy
from weighted_graph import WeightedGraph

class DBM(WeightedGraph):

    def __init__(self):
        self.outgoings = {}
        self.incomings = {}

    def copy(self):
        ''' Return a copy of the DBM. '''
        result = DBM()
        result.outgoings = {}
        for node in self.outgoings:
            result.outgoings[node] = set(self.outgoings[node])
        result.incomings = {}
        for node in self.incomings:
            result.incomings[node] = set(self.incomings[node])
        return result

    def set_weight(self, source, weight, target):
        ''' Set the weight between source and target to weight. Can also
        be None (= infinite weight). '''
        if source not in self.outgoings:
            self.outgoings[source] = set()
            self.incomings[source] = set()
        if target not in self.outgoings:
            self.outgoings[target] = set()
            self.incomings[target] = set()
        found = False
        for (existing_weight, existing_target) in self.outgoings[source]:
            if existing_target == target:
                self.outgoings[source].remove((existing_weight, existing_target))
                if weight is not None:
                    self.outgoings[source].add((weight, target))
                found = True
                break
        if not found and weight is not None:
            self.outgoings[source].add((weight, target))
        found = False
        for (existing_source, existing_weight) in self.incomings[target]:
            if existing_source == source:
                self.incomings[target].remove((existing_source, existing_weight))
                if weight is not None:
                    self.incomings[target].add((source, weight))
                found = True
                break
        if not found and weight is not None:
            self.incomings[target].add((source, weight))
    
    def all_nodes(self):
        ''' Get a copy of the list of all occuring nodes. '''
        return self.outgoings.keys()[:]

    def incomings(self, node):
        ''' Get all incoming edges from node. '''
        return self.incomings[node]
    
    def outgoings(self, node):
        ''' Get all outgoing edges from node. '''
        return self.outgoings[node]

    def get_weight(self, source, target):
        ''' Get the weight of the edge between source and target,
        None for infinite weight. '''
        if source not in self.outgoings or target not in self.outgoings:
            return None
        for (weight, existing_target) in self.outgoings[source]:
            if existing_target == target:
                return weight
        return None
    
    def exists_negative_cycle(self):
        ''' Return true if a negative cycle exists in the DBM. '''
        # add an artificial node None
        distance = {}
        predecessor = {}
        # Apply Bellman-Ford algorithm
        self.set_weight(None, 0, None)
        # side effect: None is added as known node,
        # no problem with iteration over self.outgoings
        for node in self.outgoings:
            self.set_weight(None, 0, node)
            # init dicts
            distance[node] = None
            predecessor[node] = None
        distance[None] = 0
        i = len(self.outgoings.keys())-1
        while(i > 0):
            # iterate all edges
            for source in self.outgoings:
                for (weight, target) in self.outgoings[source]:
                    if weight is None:
                        continue # to be sure...
                    source_distance = distance[source]
                    target_distance = distance[target]
                    if source_distance is None:
                        continue
                    elif (target_distance is None
                          or source_distance + weight < target_distance):
                        distance[target] = distance[source] + weight
                        predecessor[target] = source
            i -= 1
        # check for cycles
        negative_cycle = False
        for source in self.outgoings:
            for (weight, target) in self.outgoings[source]:
                source_distance = distance[source]
                target_distance = distance[target]
                if source_distance is None:
                    continue
                elif (target_distance is None
                      or source_distance + weight < target_distance):
                    negative_cycle = True
                    break
        for node in self.outgoings:
            if node is not None:
                self.set_weight(None, None, node)
        return negative_cycle
                
    def find_shortest_paths(self):
        ''' Return a DBM with shortest path weights as entries. '''
        sp = self.copy()
        i = 1

        def add_weights(w1, w2):
            if w1 is None or w2 is None:
                return None
            else:
                return w1 + w2

        def min_extended(m1, m2):
            if m1 is None:
                return m2
            elif m2 is None:
                return m1
            return min(m1, m2)
        
        for node in self.outgoings:
            for source in self.outgoings:
                for target in self.outgoings:
                    distance = min_extended(
                        sp.get_weight(source, target),
                        add_weights(sp.get_weight(source, node),
                                    sp.get_weight(node, target)))
                    sp.set_weight(source,
                                  distance,
                                  target)
        # adjust diagonals
        for node in self.outgoings:
            sp.set_weight(node, 0, node)
        return sp           
        
    def to_string(self):
        ''' Get a textual representation of the DBM graph. '''
        result = ''
        for node in self.outgoings:
            if node is None:
                continue # private node
            result += 'node: %s\n' % node
            for (weight, target) in self.outgoings[node]:
                result += '%s -(%s)-> %s\n' % (node, weight, target)
            for (source, weight) in self.incomings[node]:
                result += '%s <=(%s)= %s\n' % (node, weight, source)
        return result
    
    def __hash__(self):
        ''' Return a hash value for DBM. '''
        p = 997
        a = 123
        hash = 0
        for source in self.outgoings:
            hash = (hash + a) % p
            for (weight, target) in self.outgoings[source]:
                if weight:
                    hash = (hash + weight*a) %  p
                    # hash = (hash + hash(target)*a) % p
        return hash

    def __eq__(self, other):
        ''' Return True iff other is self. '''
        if isinstance(other, self.__class__):
            return self.outgoings == other.outgoings
        else:
            return False
