##############################
#
# variables.py 
#
# Variable representation
#
# (C) 2016, Andreas Gaiser
##############################

from type_system import *

class Variable(object):
    ''' Variable class '''
    
    def __init__(self, identifier, type):
        ''' identifier has to be hashable and unique. '''
        assert isinstance(type, Type)
        self.id = identifier
        self.type = type
        
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.id == other.id
        else:
            return False

    def __str__(self):
        return '%s{type: %s}' % (self.id, self.type)
        
