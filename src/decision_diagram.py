###########################################
#
# decision_diagram.py
# 
# Decision Diagram Element 
#
#
# (C) 2016, Andreas Gaiser
###########################################


import numbers
import domain_factory

class DecisionDiagram(object):
    
    def __init__(self, inner_element, hi, lo):
        ''' Do not use the constructor explicitly; it
        is only used by the factory to allocate node instances.'''
        self.value = inner_element
        self.hi = hi
        self.lo = lo
        
    # Instance methods

    def is_leaf(self):
        return (self.hi is None
                and self.lo is None)

    def is_inner(self):
        return not self.is_leaf()

    def get_hi(self):
        return self.hi

    def get_lo(self):
        return self.lo

    def get_inner_value(self):
        return self.value
    
    def get_variable(self):
        if self.is_leaf():
            return None
        else:
            return self.value

    def get_value(self):
        if self.is_leaf():
            return self.value
        else:
            return None

    
        
                    
