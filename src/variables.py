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
        
i1 = Integer(0, 127)
i2 = Integer(0, 127)
p = Pointer(Pointer(i1))
p2 = Pointer(Pointer(i2))

v = Variable('x',p)
hash(v)
v == v
d = {}
print p == p2
d[p] = True
if p in d:
    print "UI :)"
t = TypeStore()
print (t.register(p) == p2)
