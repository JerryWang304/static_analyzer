###########################################
#
# dbms.py 
#
# Difference bound matrices domain
#
# (C) 2016, Andreas Gaiser
###########################################


import numbers
import dbm

class DBMFactory():

    #
    # Private methods
    #

    def __init__(self, DEFAULT_MAX_VALUE, DEFAULT_MIN_VALUE):
        self.variables = {}
        self.DEFAULT_MAX_VALUE = DEFAULT_MAX_VALUE
        self.DEFAULT_MIN_VALUE = DEFAULT_MIN_VALUE
        self.constants = []
        
    def _intersect(self, tuple1, tuple2):
        (l1, r1) = tuple1
        (l2, r2) = tuple2
        if r1 < l1 or r2 < l2:
            return None
        return (max(l1, l2), min(r1, r2))
        
    def _interval(self, element, variable):
        if element is None:
            return None
        if variable in element:
            return element[variable]
        else:
            return self.variables[variable]

    def _normalize(self, element):
        if element is None:
            return None
        return element.find_shortest_paths()
 
    def _copy(self, element):
        if element is None:
            return None
        result = {}
        for variable in element:
            result[variable] = element[variable]
        return result

    def _is_in(self, scalar, element):
        if element is None:
            return False
        (l, r) = element
        return (l <= scalar and r >= scalar)
            
    #
    # Public methods
    #
    
    def add_var(self, variable, max_val, min_val):
        self.variables[variable] = (max_val, min_val)
        
    def get_top(self):
        return dbm.DBM()

    def get_bot(self):
        return None

    def add_constant(self, constant):
        self.constants.append(constant)
        self.constants = sorted(self.constants)
    
    def is_subseteq(self, element1, element2):
        if element1 is None:
            return True
        if element2 is None:
            return False
        s1 = self._normalize(element1)
        s2 = self._normalize(element2)
        common_vars = []
        for v in self.variables():
            if v in s1.all_nodes() or v in s2.all_nodes():
                common_vars.append(v)
        for v1 in common_vars:
            for v2 in common_vars:
                if s1.get_weight(v1, v2) > s2.get_weight(v1, v2):
                    return False
        return True
                
    def is_eq(self, element1, element2):
        if element1 is None:
            return element2 is None
        
        s1 = self._normalize(element1)
        s2 = self._normalize(element2)
        common_vars = []
        for v in self.variables():
            if v in s1.all_nodes() or v in s2.all_nodes():
                common_vars.append(v)
        for v1 in common_vars:
            for v2 in common_vars:
                if s1.get_weight(v1, v2) != s2.get_weight(v1, v2):
                    return False
        return True
        
    def union(self, element1, element2):
        result = dbm.DBM()

        if element1 is None:
            return element2.copy()
        elif element2 is None:
            return element1.copy()

        def max_extended(m1, m2):
            if m1 is None or m2 is None:
                return None
            return max(m1, m2)

        common_vars = []
        for v in self.variables():
            if v in s1.all_nodes() or v in s2.all_nodes():
                common_vars.append(v)
        for v1 in common_vars:
            for v2 in common_vars:
                result.set_weight(
                    v1,
                    max_extended(element1.get_weight(v1, v2),
                                 element2.get_weight(v1, v2)),
                    v2)
        return result

    def intersect(self, element1, element2):
        result = dbm.DBM()

        if element1 is None:
            return element2.copy()
        elif element2 is None:
            return element1.copy()

        def min_extended(m1, m2):
            if m1 is None:
                return m2
            elif m2 is None:
                return m1
            return min(m1, m2)

        common_vars = []
        for v in self.variables():
            if v in s1.all_nodes() or v in s2.all_nodes():
                common_vars.append(v)
        for v1 in common_vars:
            for v2 in common_vars:
                result.set_weight(
                    v1,
                    min_extended(element1.get_weight(v1, v2),
                                 element2.get_weight(v1, v2)),
                    v2)
        return result

    def is_literal(self, value):
        return isinstance(value, numbers.Number) 
    
    def op_load_constant(self, element, target_var, constant):
        '''
        strongest postcondition of
        variable := constant
        '''
        if element is None:
            return None
        result = self._copy(element)
        # todo: what if constant not in range(variable)?
        result[target_var] = (constant, constant)
        return self._normalize(result)

    def op_binary(self,
                  element,
                  operator,
                  target_var,
                  op1,
                  op2):
        if element is None:
            return None
        if self.is_literal(op1):
            i1 = (op1, op1)
        else:
            i1 = self._interval(element, op1) 
        if self.is_literal(op2):
            i2 = (op2, op2)
        else:
            i2 = self._interval(element, op2)
        return self.op_binary_intervals(element,
                                        operator,
                                        target_var,
                                        i1,
                                        i2)
    
            
    def op_binary_intervals(self,
                            element,
                            operator,
                            target_var,
                            interval1,
                            interval2):
        '''
        strongest postcondition of
        variable := i1 (+) i2
        '''
        if element is None:
            return None
        result = self._copy(element)
        # todo: what if result not in range?
        (l1, r1) = interval1
        (l2, r2) = interval2
        cl = None
        cr = None
        if operator == '*':
            # maybe switch (negative numbers)
            (cl, cr) = (min(l1*l2, r1*r2, l1*r2, l2*r1),
                        max(l1*l2, r1*r2, l1*r2, l2*r1))
        elif operator == '+':
            (cl, cr) = (l1+l2, r1+r2)
        elif operator == '-':
            (cl, cr) = (l1-l2, r2-l2)
        elif operator == '%':
            # i2 contains 1 integer
            if r2-l2 == 0 and r2 == 0:
                print "Division by zero!"
                return None
            elif r2-l2 == 0 and r1-l1 == 0:
                (cl, cr) = (r1 % r2, r1 % r2)
            else:
                max_el = max(abs(l2), abs(r2))-1
                if l1 >= 0:
                    (cl, cr) = (0, max_el)
                else:
                    (cl, cr) = (-max_el, max_el)
                    
            if l2 <= 0 and 0 <= r2:
                print "Possible Division by zero!"
        else:
            print 'Wrong operator!'
        if cl is not None or cr is not None:
            result[target_var] = (cl, cr)
        else:
            result[target_var] = self.variables[target_var]
        return self._normalize(result)

    
    def cond_binary(self,
                    element,
                    operator,
                    op1,
                    op2):
        '''
        strongest postcondition of
        (variable (=) variable)
        '''
        if element is None:
            return None

        if operator == '>' :
            return self.cond_binary(element, '<', op2, op1)
        elif operator == '>=' :
            return self.cond_binary(element, '<=', op2, op1)
        result = self._copy(element)
        i1 = None
        i2 = None
        left_var = None
        right_var = None
        if self.is_literal(op1):
            i1 = (op1, op1)
        else:
            i1 = self._interval(element, op1)
            left_var = op1
        if self.is_literal(op2):
            i2 = (op2, op2)
        else:
            i2 = self._interval(element, op2)
            right_var = op2
            
        (l1, r1) = i1
        (l2, r2) = i2
        
        if operator == '==':
            buffer = self._intersect((l1, r1), (l2, r2))
            if buffer is None:
                return None
        elif operator == '!=':
            if op1 == op2:
                return None
            if (l1 - r1) == 0 and (l2-r2) == 0 and (l1 == l2):
                return None

        new_i1 = None
        new_i2 = None
        if operator == '<=':
            if r2 < l1:
                return None
            new_i1 = (l1, min(r1, r2))        
            new_i2 = (max(l1, l2), r2)
        elif operator == '<':
            if op1 == op2:
                return None
            if r2 <= l1:
                return None
            new_i1 = (l1, min(r1, r2-1))        
            new_i2 = (max(l1, l2+1), r2)
        else:
            print 'Unknown operator: %s ' % operator
            
        if new_i1 and left_var:
            result[left_var] = new_i1
        if new_i2 and right_var:
            result[right_var] = new_i2
        
        return self._normalize(result)
    
    def widen(self, element1, element2):
        result = dbm.DBM()
                
        if element1 is None:
            return element2.copy()
        elif element2 is None:
            return element1.copy()

        common_vars = []
        for v in self.variables():
            if v in s1.all_nodes() or v in s2.all_nodes():
                common_vars.append(v)
        for v1 in common_vars:
            for v2 in common_vars:
                val1 = element1.get_weight(v1, v2)
                val2 = element2.get_weight(v1, v2)
                if val1 is None or val2 is None or val2 > val1:
                    result.set_weight(v1, None, v2)
                else:
                    result.set_weight(v1, val2, v2)
        return result
    
    def to_string(self, element):
        if element is None:
            return '<BOT>'
        elif len(element) == 0:
            return '<TOP>'
        result = '['
        keys_sorted = sorted(element.keys())
        for variable in keys_sorted:
            result += ('%s in [%s, %s], '
                       % (variable,
                          element[variable][0],
                          element[variable][1]))
        if result.endswith(', '):
            result = result[:-2]
        result += ']'
        return result

