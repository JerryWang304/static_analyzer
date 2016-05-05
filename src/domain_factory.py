####################################
#
# domain_factory.py 
#
# base class for domain factories
#
# (C) 2016, Andreas Gaiser
####################################

import abc

class DomainFactory(object):

    __metaclass__ = abc.ABCMeta

    # Variable handling
    
    @abc.abstractmethod
    def add_integer_var(self, variable, min_val, max_val):
        ''' Add a integer variable to the factory, 
        variable being its unique identifier. '''
        return

    @abc.abstractmethod
    def add_bool_var(self, variable):
        ''' Add a boolean variable to the factory, 
        variable being its unique identifier. '''
        return

    
    # I/O

    @abc.abstractmethod
    def to_string(self, element):
        ''' Return a string representation of "element". '''
        return
    

    # Algebraic operations
    
    @abc.abstractmethod
    def get_top(self):
        ''' Get an instance of the top element. '''
        return

    @abc.abstractmethod
    def get_bot(self):
        ''' Get an instance of the bottom element. '''
        return

    @abc.abstractmethod
    def is_subseteq(self, element1, element2):
        ''' Return true iff "element1 <= element2" for two
        abstract elements, "<=" being the abstract partial order. '''

    @abc.abstractmethod
    def is_eq(self, element1, element2):
        ''' Return true iff both elements are representing
        the same set of concrete states. '''

    @abc.abstractmethod
    def union(self, element1, element2):
        ''' Return the abstract union of "element1" and "element2". '''
        return
    
    @abc.abstractmethod
    def intersect(self, element1, element2):
        ''' Return the abstract intersection of "element1" and "element2". '''
        return

    @abc.abstractmethod
    def widen(self, element1, element2):
        ''' Return a widening value for arguments element1 and element2. '''
        return
    
    # Semantics of the abstract machine

    @abc.abstractmethod
    def op_load_constant(self, element, target_var, constant):
        ''' Return strongest postcondition of "target_var := constant" applied
        to element. '''
        return
    
    @abc.abstractmethod
    def op_binary(self, element, operator, target_var, op1, op2):
        ''' Return strongest postcondition of "target_var = op1 operator op2" applied
        to element. '''
        return
        
    @abc.abstractmethod
    def cond_binary(self, element, operator, op1, op2):
        ''' Return strongest postcondition of condition "op1 operator op2" applied
        to element. '''
        return
        
