####################################
#
# pointer_values.py 
#
# simple points-to analysis.
#
# (C) 2016, Andreas Gaiser
####################################

import domain_factory

class PointerValueDomainFactory(domain_factory.DomainFactory):

    def __init__(self):
        self._loc_counter = 1
        self._locations_to_id = {}
        self._id_to_locations = {}
        self._uninit_counter = 1
        self._uninit_to_id = {}
        self._id_to_uninit = {}
        self._points_to = {}
        
    def add_variable(self, variable):
        self._uninit_to_id[variable] = self._uninit_counter
        self._id_to_uninit[self._uninit_counter] = variable
        self._uninit_counter += 1
        
    def add_integer_var(self, variable, min_val, max_val):
        self.add_variable(variable)

    def add_bool_var(self, variable):
        self.add_variable(variable)

    def add_location(self, location):
        self._locations[location] = self._loc_counter
        self._id_to_locations[self._loc_counter] = location
        self._loc_counter += 1
        
    # I/O

    def to_string(self, element):
        return ''

    # Algebraic operations
    
    @abc.abstractmethod
    def get_top(self):
        return None

    @abc.abstractmethod
    def get_bot(self):
        return None

    @abc.abstractmethod
    def is_subseteq(self, element1, element2):
        ''' Return true iff "element1 <= element2" for two
        abstract elements, "<=" being the abstract partial order. '''
        return
    
    @abc.abstractmethod
    def is_eq(self, element1, element2):
        ''' Return true iff both elements are representing
        the same set of concrete states. '''
        return
    
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
    def op_load_variable(self, element, target_var, source_var):
        ''' Return strongest postcondition of "target_var := source_var" applied
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
        
    @abc.abstractmethod
    def project_var(self, element, variable):
        ''' Remove information about variable. '''
        return
