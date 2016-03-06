import abc


class WeightedGraph(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def all_nodes(self):
        ''' Return the set of nodes in the graph. '''
        return

    @abc.abstractmethod
    def incomings(self, node):
        ''' Return the set of edges having as target the given node,
        as tuples (w, n), where w is the weight of the edge
        and n the target node. '''
        return

    @abc.abstractmethod
    def outgoings(self, node):
        ''' Return the set of edges having as source the given node,
        as tuples (n, w), where w is the weight of the edge
        and n the source node. '''
        return

    @abc.abstractmethod
    def get_weight(self, source, target):
        ''' Get weight between the two given nodes. Returns None if no
        weight is specified '''
        return

    @abc.abstractmethod
    def set_weight(self, source, weight, target):
        ''' Set weight between the two given nodes. 
        None specifies infinite weight. '''
        return
