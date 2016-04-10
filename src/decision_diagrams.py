###########################################
#
# decision_diagrams.py
#
# Domain factory for decision diagrams
#
# (C) 2016, Andreas Gaiser
###########################################

import weakref
import numbers
from domain_factory import DomainFactory
from decision_diagram import DecisionDiagram

class DecisionDiagramFactory(DomainFactory):

    def _init_tables(self):
        # Leaf values are stored separately with NEGATIVE indices
        self._LEAVES = {} # >>> weakref.WeakValueDictionary()
        self._LEAVES[-1] = self._bot
        self._LEAVES[-2] = self._top
        self._DOMAIN_ELEMENTS = {} # >>> weakref.WeakValueDictionary()
        self._DOMAIN_ELEMENTS[self._bot.get_value()] = self._bot
        self._DOMAIN_ELEMENTS[self._top.get_value()] = self._top
        # _H_TABLE: (VARIABLE, LEFT, RIGHT) -->  DecisionDiagram
        # _T_TABLE: DecisionDiagram --> (VARIABLE, LEFT, RIGHT):
        # DONE VIA elements in the DecisionDiagram element
        self._H_TABLE = {} # >>> weakref.WeakValueDictionary()
        self._H_TABLE[(-1, None, None)] = self._bot
        self._H_TABLE[(-2, None, None)] = self._top
        self._free_leaf_pos = -3
                      
    def _lookup(self, inner_value, left, right):
        # is the element a domain element?
        if (left is None and right is None):
                # check for the inner_value in the domain element hash
                try:
                    return self._DOMAIN_ELEMENTS[inner_value]
                except KeyError:
                    pass
        else:
            try:
                return self._H_TABLE[(inner_value, left, right)]
            except KeyError:
                pass
        return None

    def _add_or_get(self, inner_value, left, right):
        result = self._lookup(inner_value, left, right)  
        if result is None:
            result = DecisionDiagram(inner_value, left, right)
            self._H_TABLE[(inner_value, left, right)] = result
            if left is None and right is None:
                self._DOMAIN_ELEMENTS[inner_value] = result
        return result

    def _is_in(self, inner_value, left, right):
        return _lookup(inner_value, left, right) is not None
                          
    def _mk(self, inner_value, left, right):
        if (left == right) and left is not None:
            return left
        else:
            return self._add_or_get(inner_value, left, right)
                          
    def __init__(self, inner_factory):
        self.inner_factory = inner_factory
        self.variables = {}
        self._var_index = 0
        self._bot = DecisionDiagram(inner_factory.get_bot(), None, None)
        self._top = DecisionDiagram(inner_factory.get_top(), None, None)
        self._init_tables()
                          
    def _var_predecessor(self, var1, var2):
        return self.variables[var1] < self.variables[var2]
                          
    def _compare_diagrams(self, first, second, relation):
        if first.is_leaf() and second.is_leaf():
            return relation(first.get_value(), second.get_value())
        elif first.is_leaf():
            return (self._compare_diagrams(first,
                                           second.get_hi(),
                                           relation)
                    and
                    self._compare_diagrams(first,
                                           second.get_lo(),
                                           relation))
        elif second.is_leaf():
            return (self._compare_diagrams(first.get_hi(),
                                           second,
                                           relation)
                    and
                    self._compare_diagrams(first.get_lo(),
                                           second,
                                           relation))
        # first and second are inner nodes of a diagram
        first_var = first.get_variable()
        second_var = second.get_variable()
        if first_var == second_var:
            true_cond = self._compare_diagrams(first.get_hi(),
                                               second.get_lo(),
                                               relation)
            if not true_cond:
                return False
            return self._compare_diagrams(first.get_lo(),
                                          second.get_lo(),
                                          relation)
        elif self._var_predecessor(first_var, second_var):
            # first_var comes before second_var
            true_cond = self._compare_diagrams(first.get_hi(),
                                               second,
                                               relation)
            if not true_cond:
                return False
            return self._compare_diagrams(first.get_lo(),
                                          second,
                                          relation)
        else:
            # second_var comes before first_var
            true_cond = self._compare_diagrams(first,
                                               second.get_hi(),
                                               relation)
            if not true_cond:
                return False
            return self._compare_diagrams(first.get_lo(),
                                          second.get_lo(),
                                          relation)

    def _set_to(self, element, variable, value):
        assert value in (0, 1)
        if (element.is_leaf() or
            self._var_predecessor(variable, element.get_variable())):
            if value == 0:
                return self._mk(variable, self._bot, element)
            else:
                return self._mk(variable, element, self._bot)
        else:
            element_var = element.get_variable()
            if element_var == variable:
                if value == 0:
                    return self._mk(variable,
                                    self._bot,
                                    self.union(element.get_hi(),
                                               element.get_lo()))
                else:
                    return self._mk(variable,
                                    self.union(element.get_hi(),
                                               element.get_lo()),
                                    self._bot)
            else:
                # variable < element_var
                return self._mk(element_var,
                                self._set_to(element.get_hi(),
                                              variable,
                                              value),
                                self._set_to(element.get_lo(),
                                              variable,
                                              value))

    def _negate_operator(self, op):
        if (op == '=='):
            return '!='
        if (op == '!='):
            return '=='
        if (op == '<='):
            return '>'
        if (op == '<'):
            return '>='
        if (op == '>='):
            return '<'
        if (op == '>'):
            return '<='
        return op

    def _transform_leaves(self, element, transformer):
        if element.is_leaf():
            return self._mk(transformer(element.get_value()), None, None)
        else:
            return self._mk(element.get_variable(),
                            self._transform_leaves(element.get_hi(), transformer),
                            self._transform_leaves(element.get_lo(), transformer))
        
    def _propagate(self, element, variable, pos_transformer, neg_transformer):
        if element.is_leaf():
            value = element.get_value()
            hi = self._mk(pos_transformer(value), None, None)
            lo = self._mk(neg_transformer(value), None, None)
            return self._mk(variable, hi, lo)
        elif (element.get_variable() == variable
              or self._var_predecessor(variable, element.get_variable())):
            hi = self._transform_leaves(element.get_hi(), pos_transformer)
            lo = self._transform_leaves(element.get_lo(), neg_transformer)
            return self._mk(variable, hi, lo)
        else:
            # propagate to the leaves
            hi = self._propagate(element.get_hi(), pos_transformer, neg_transformer)
            lo = self._propagate(element.get_lo(), pos_transformer, neg_transformer)
            return self._mk(element.get_variable(), hi, lo)

            
    def _mk_op_leaves(self, element, op):
        if element.is_leaf():
            return self._mk(op(element.get_value()), None, None)
        else:
            return self._mk(element.get_variable(),
                            self._mk_op_leaves(element.get_hi(), op),
                            self._mk_op_leaves(element.get_lo(), op))
                            
    def _mk_op_binary(self, first, second, op):
        if first.is_leaf() and second.is_leaf():
            return self._mk(op(first.get_value(), second.get_value()),
                            None,
                            None)
        elif first.is_leaf():
            return self._mk(second.get_variable(),
                            self._mk_op_binary(first,
                                        second.get_hi(),
                                        op),
                            self._mk_op_binary(first,
                                        second.get_lo(),
                                        op))
        elif second.is_leaf():
            return (self._mk(first.get_variable(),
                             self._mk_op_binary(first.get_hi(),
                                         second,
                                         op),
                            self._mk_op_binary(first.get_lo(),
                                        second,
                                        op)))
        # else: first and second are inner nodes of a diagram
        first_var = first.get_variable()
        second_var = second.get_variable()
        if first_var == second_var:
            return (self._mk(first_var,
                             self._mk_op_binary(first.get_hi(),
                                         second.get_hi(),
                                         op),
                             self._mk_op_binary(first.get_lo(),
                                         second.get_lo(),
                                         op)))
        elif self._var_predecessor(first_var, second_var):
            # first_var comes before second_var
            return (self._mk(first_var,
                             self._mk_op_binary(first.get_hi(),
                                         second,
                                         op),
                             self._mk_op_binary(first.get_lo(),
                                         second,
                                         op)))
        else:
            return (self._mk(first_var,
                             self._mk_op_binary(first,
                                         second.get_hi(),
                                         op),
                             self._mk_op_binary(first,
                                         second.get_lo(),
                                         op)))
        
    # Public methods
    # Variable handling
            
    def add_integer_var(self, variable, min_val, max_val):
        self.inner_factory.add_integer_var(variable, min_val, max_val)
        
    def add_bool_var(self, variable):
        self.variables[variable] = self._var_index
        self._var_index += 1

    def add_constant(self, constant):
        self.inner_factory.add_constant(constant)
        
    # I/O
    def to_string(self, element):
        if element.is_leaf():
            return 'LEAF: %s' % self.inner_factory.to_string(element.get_value())
        else:
            return 'IF %s THEN %s else %s' % (element.get_variable(),
                                              self.to_string(element.get_hi()),
                                              self.to_string(element.get_lo()))

    # Algebraic operations
        
    def get_top(self):
        return self._top
        
    def get_bot(self):
        return self._bot
            
    def is_subseteq(self, element1, element2):
        return self._compare_diagrams(element1, element2,
                                      lambda x, y: self.inner_factory.is_subseteq(x, y))
                
    def is_eq(self, element1, element2):
        return self._compare_diagrams(element1, element2,
                                      lambda x, y: self.inner_factory.is_eq(x, y))
    
    def union(self, element1, element2):
        return self._mk_op_binary(element1, element2,
                                  lambda x, y: self.inner_factory.union(x, y))

    def intersect(self, element1, element2):
        return self._mk_op_binary(element1, element2,
                                  lambda x, y: self.inner_factory.intersect(x, y))
    
    def widen(self, element1, element2):
        return self._mk_op_binary(element1, element2,
                                  lambda x, y: self.inner_factory.widen(x, y))

    # Semantics of the abstract machine
    
    def op_load_constant(self, element, target_var, constant):
        if target_var in self.variables:
            # target_var is a (boolean) decision var
            # this means: constant is either 0 or 1
            assert constant in (0, 1)
            return self._set_to(element, target_var, constant)
        else:
            return self._mk_op_leaves(element,
                                      lambda x: self.inner_factory.load_constant(x, target_var, constant))

    def _is_boolean_operator(self, op):
        return op in [ "==", "!=", "<", "<=", ">", ">=" ]
        
    def op_binary(self,
                  element,
                  operator,
                  target_var,
                  op1,
                  op2):
        if (self._is_boolean_operator(operator)
            and target_var in self.variables):
            # decision variable
            # x = (a < b)
            # x --> (a < b)
            # !x --> (a >= b)
            pos_transformer = (lambda x:
                               self.inner_factory.cond_binary(x,
                                                              operator,
                                                              op1,
                                                              op2))
            neg_transformer = (lambda x:
                               self.inner_factory.cond_binary(x,
                                                              self._negate_operator(operator),
                                                              op1,
                                                              op2))
            return self._propagate(element,
                                   target_var,
                                   pos_transformer,
                                   neg_transformer)

        else:
            transformer = (lambda x:
                           self.inner_factory.op_binary(x,
                                                        operator,
                                                        target_var,
                                                        op1,
                                                        op2))
            # just transform the leaves
            return self._transform_leaves(element, transformer)
                                          
    def cond_binary(self,
                    element,
                    operator,
                    op1,
                    op2):
        # TODO: right now only numerical comparisons
        transformer = (lambda x:
                       self.inner_factory.cond_binary(x,
                                                      operator,
                                                      op1,
                                                      op2))
        return self._transform_leaves(element, transformer)                      



from dbms import *

# TEST CASE:
#
# c1, c2
# x1, x2

# c1 = x1 < 5
# c2 = x1 >= x2

##########################

inner = DBMFactory(-100, 100)
inner.add_integer_var('x1', -512, 512)
inner.add_integer_var('x2', -512, 512)

domain = DecisionDiagramFactory(inner)
domain.add_bool_var('c1')
domain.add_bool_var('c2')


e1 = domain.get_top()
e1 = domain.op_binary(e1, '<', 'c1', 'x1', 5)
print domain.to_string(e1)
e2 = domain.cond_binary(e1, '>=', 'x1', 'x2')
print domain.to_string(e2)
e3 = domain._set_to(e2, 'c1', 1) 
print domain.to_string(e3)
