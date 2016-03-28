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

class DecisionTreeFactory():

    #
    # Private methods
    #

    def __init__(self, variable_order):
        self.variables = {}
        self.DEFAULT_MAX_VALUE = DEFAULT_MAX_VALUE
        self.DEFAULT_MIN_VALUE = DEFAULT_MIN_VALUE
        self.constants = []
        self.variables[0] = (0, 0)
        
    def _intersect(self, tuple1, tuple2):
        (l1, r1) = tuple1
        (l2, r2) = tuple2
        if r1 < l1 or r2 < l2:
            return None
        return (max(l1, l2), min(r1, r2))
        
    def _interval(self, element, variable):
        # variable - 0 <= W
        # variable <= W
        right = element.get_weight(variable, 0)
        left = element.get_weight(0, variable)
        if right is None:
            right = self.variables[variable][1]
        if left is None:
            left = self.variables[variable][0]
        else:
            left = -left
        return (left, right)
            
    def _normalize(self, element):
        if element is None:
            return None
        if element.exists_negative_cycle():
            return None
        return element.find_shortest_paths()
 
    def _copy(self, element):
        if element is None:
            return None
        return element.copy()
    
    def _is_in(self, scalar, element):
        if element is None:
            return False
        (l, r) = element
        return (l <= scalar and r >= scalar)

    def _forget_destructive(self, value, variable):
        result = value

        def min_extended(m1, m2):
            if m1 is None:
                return m2
            elif m2 is None:
                return m1
            return min(m1, m2)
        
        for i in value.all_nodes():
            for j in value.all_nodes():
                if i == j and j == variable:
                    result.set_weight(i, 0, j)
                elif i != variable and j != variable:
                    w1 = value.get_weight(i, variable)
                    w2 = value.get_weight(variable, j)
                    w3 = value.get_weight(i, j)
                    if w1 is None or w2 is None:
                        result.set_weight(i, value.get_weight(i, j), j)
                    else:
                        result.set_weight(i,
                                          min_extended(w1+w2, w3),
                                          j)
                else:
                    result.set_weight(i, None, j)
        return result

    
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
        s1 = self._normalize(element1)
        s2 = self._normalize(element2)
        if s1 is None:
            return True
        if s2 is None:
            return False
        common_vars = []
        for v in self.variables:
            if v in s1.all_nodes() or v in s2.all_nodes():
                common_vars.append(v)
        for v1 in common_vars:
            for v2 in common_vars:
                w2 = s2.get_weight(v1, v2)
                if w2 is None:
                    continue
                w1 = s1.get_weight(v1, v2)
                if w1 is None:
                    return False
                if s1.get_weight(v1, v2) > s2.get_weight(v1, v2):
                    return False
        return True
                
    def is_eq(self, element1, element2):
        
        s1 = self._normalize(element1)
        s2 = self._normalize(element2)
        if s1 is None:
            return s2 is None
        if s2 is None:
            return False

        common_vars = []
        for v in self.variables:
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
            if element2 is None:
                return None
            return element2.copy()
        elif element2 is None:
            return element1.copy()

        def max_extended(m1, m2):
            if m1 is None or m2 is None:
                return None
            return max(m1, m2)

        common_vars = []
        for v in self.variables:
            if v in element1.all_nodes() or v in element2.all_nodes():
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
        for v in self.variables:
            if v in element1.all_nodes() or v in element2.all_nodes():
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
        result = self._forget_destructive(element.copy(), target_var)
        return self._guard(self._guard(result, target_var, 0, constant),
                           0, target_var, -constant)
    
    def op_binary(self,
                  element,
                  operator,
                  target_var,
                  op1,
                  op2):
        if element is None:
            return None
        # special case: x = y + c
        if operator == '+' and self.is_literal(op2):
            # forget x, then add: x - y <= c AND y - x <= -c
            forget_element = self._forget_destructive(element, target_var)
            result = self._guard(self._guard(forget_element,
                                             target_var, op1, op2),
                                 op1, target_var, -op2)
            return result
        # elif operator == '+' and self.is_literal(op1):

        # TODO: op1 == target_var etc.
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
    
    # x = y + z
    # <=>
    # x - y = z
    # => x - y >= max(z)
    # => x - y >= min(z)
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

        # forget target var...
        result = self._forget_destructive(element.copy(), target_var)
            
        if cl is not None:
            result.set_weight(0, -cl, target_var)
        if cr is not None:
            result.set_weight(target_var, cr, 0)
            
        return self._normalize(result)


    def _guard(self, element, x, y, c):
        ''' Effect x - y <= c on element. '''
        result = self._copy(element)
        weight = element.get_weight(x, y)
        if weight is None or c < weight:
            result.set_weight(x, c, y)
        return result
    
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
        # TODO '==' and '!='
        elif operator == '==' :
            return self.cond_binary(self.cond_binary(element, '<=', op1, op2), '>=', op1, op2)
        elif operator == '!=':
            # TODO: more preices
            return self._copy(element)
        
        result = self._copy(element)
        
        # standard form:
        #     x <= y
        # <=> x - y <= 0
        x = op1
        y = op2
        
        # x < y <=> x <= y - 1  <=> x - y <= -1
        offset = -1 if operator == '<' else 0 
        if self.is_literal(op1):
            # c1 - y <= 0
            # <=> -y <= - c1
            # <=> 0 - y <= - c1
            return self._guard(element, 0, op2, -op1 + offset)
        elif self.is_literal(op2):
            # x - c2 <= c
            # x - 0  <= c2
            return self._guard(element, op1, 0, op2 + offset)
        else:
            return self._guard(element, op1, op2, offset)
    
    def widen(self, element1, element2):
        result = dbm.DBM()
                
        if element1 is None:
            if element2 is None:
                return None
            return element2.copy()
        elif element2 is None:
            return element1.copy()

        s1 = self._normalize(element1)
        s2 = self._normalize(element2)
        
        common_vars = []
        for v in self.variables:
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
        element = self._normalize(element)
        
        if element is None:
            return '<BOT>'
        #elif len(element.variables) == 0:
        #    return '<TOP>'
        
        result = '[\n'
        for v1 in self.variables:
            for v2 in self.variables:
                d = element.get_weight(v1, v2)
                if d is not None:
                    result += "%s - %s <= %s\n" % (v1, v2, d)
                    
        result += ']\n'
        return result

