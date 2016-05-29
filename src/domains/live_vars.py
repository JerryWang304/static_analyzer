##############################
#
# live_vars.py 
#
# live variables domain
#
# (C) 2016, Andreas Gaiser
##############################

import domain_factory
import numbers
from BitVector import *

class LiveVarsDomainFactory(domain_factory.DomainFactory):
    
    def __init__(self):
        self._variables_to_id = {}
        self._id_to_variables = {}
        self._var_index = 0

    # Private methods
    
    def _add_var(self, variable):
        self._variables_to_id[variable] = self._var_index
        self._id_to_variables[self._var_index] = variable
        self._var_index += 1

    # Variable handling
    
    def add_integer_var(self, variable, min_val, max_val):
        self._add_var(variable)

    def add_bool_var(self, variable):
        self._add_var(variable)
        
    # I/O
      
    def to_string(self, element):
        result = '{'
        index = 0
        first = True
        for bit in element:
            if bit == 1:
                if first:
                    result += '%s' % self._id_to_variables[index]
                    first = False
                else:
                    result += ', %s' % self._id_to_variables[index]
            index += 1
        result += '}'
        return result
    
    # Algebraic operations
    
    def get_top(self):
        result = BitVector(size=self._var_index)
        result.reset(1)
        print result
        print self._id_to_variables
        return result
    
    def get_bot(self):
        result = BitVector(size=self._var_index)
        result.reset(0)
        return result

    def is_subseteq(self, element1, element2):
        return element1 <= element2
    
    def is_eq(self, element1, element2):
        return element1 == element2
        
    def union(self, element1, element2):
        return element1 | element2
    
    def intersect(self, element1, element2):
        return element1 & element2
    
    def widen(self, element1, element2):
        return element1 | element2
    
    # Semantics of the abstract machine

    def op_load_constant(self, element, target_var, constant):
        # effect:
        # <START> \ { target_var }
        # target_var = constant
        # <START>
        result = element.deep_copy()
        result[self._variables_to_id[target_var]] = 0
        return result
        
    def op_binary(self, element, operator, target_var, op1, op2):
        # effect:
        # (<START> U {op1, op2}) \ { target_var }
        # target_var = op1 * op2
        # <START>
        result = element.deep_copy()
        result[self._variables_to_id[target_var]] = 0
        for op in (op1, op2):
            if op in self._variables_to_id:
                result[self._variables_to_id[op]] = 1
        return result
        
    def cond_binary(self, element, operator, op1, op2):
        # effect:
        # (<START> U {op1, op2}) 
        # condition: op1 * op2
        # <START>
        result = element.deep_copy()
        for op in (op1, op2):
            if op in self._variables_to_id:
                result[self._variables_to_id[op]] = 1
        return result
      

if __name__ == '__main__':
    dom = LiveVarsDomainFactory()
    dom.add_bool_var('x')
    dom.add_bool_var('y')
    dom.add_bool_var('z')
    print (dom.to_string(dom.get_top()))
    print (dom.to_string(dom.get_bot()))
    top = dom.get_top()
    m1 = dom.op_load_constant(top, 'x', 2)
    print (dom.to_string(m1))
    m2 = dom.op_binary(top, '+', 'y', 2, 'x')
    print (dom.to_string(m2))
