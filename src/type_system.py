##############################
#
# type_system.py 
#
# Type system of the analyzer.
#
# (C) 2016, Andreas Gaiser
##############################


class Type(object):

    def __init__(self):
        pass


class Integer(Type):

    def __init__(self,  min_value, max_value):
        super(Type, self).__init__()
        assert max_value > min_value
        self.max_value = max_value
        self.min_value = min_value

    def __str__(self):
        return 'int(range %s:%s)' % (self.min_value, self.max_value)

    def __hash__(self):
        return (123 + self.min_value*123 + self.max_value*123) % 997

    def __eq__(self, other):
        if isinstance(other, Integer):
            return ((self.min_value, self.max_value)
                    == 
                    (other.min_value, other.max_value))
        else:
            return False


class Pointer(Type):

    def __init__(self, element_type):
        super(Type, self).__init__()
        self.element_type = element_type

    def __str__(self):
        return '%s*' % self.element_type

    def __hash__(self):
        return (123 + hash(self.element_type)*123) % 997

    def __eq__(self, other):
        if isinstance(other, Pointer):
            return self.element_type == other.element_type
        else:
            return False


class TypeStore():
    ''' Serves as a cache for types. Use register(t)
    for a newly created type to get the actual "canonical" type 
    object. '''

    def __init__(self):
        self._store = {}

    def register(self, new_type):
        try:
            return self._store[new_type]
        except KeyError:
            self._store[new_type] = new_type
            return new_type
         
