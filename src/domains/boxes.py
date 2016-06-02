##############################
#
# boxes.py 
#
# Box (interval) domain
#
# (C) 2016, Andreas Gaiser
##############################

import domain_factory
import numbers

class BoxesElement:

    def __init__(self, init_ranges):
        self.ranges = init_ranges

    def __hash__(self):
        p = 997
        a = 123
        if self.ranges is None:
            return 0
        result = 0
        for v in sorted(self.ranges.keys()):
            result = (result + self.ranges[v][0]*a) % p
            result = (result + self.ranges[v][1]*a) % p
        return result

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.ranges is None and other.ranges is None:
                return True
            elif self.ranges is None or other.ranges is None:
                return False
            else:
                if len(self.ranges) != len(other.ranges):
                    return False
                else:
                    for v in self.ranges:
                        if v not in other.ranges:
                            return False
                        if other.ranges[v] != self.ranges[v]:
                            return False
            return True
        else:
            return False

class BoxDomainFactory(domain_factory.DomainFactory):

    def __init__(self, DEFAULT_MIN_VALUE, DEFAULT_MAX_VALUE):
        self.variables = {}
        self.DEFAULT_MIN_VALUE = DEFAULT_MIN_VALUE
        self.DEFAULT_MAX_VALUE = DEFAULT_MAX_VALUE
        self.constants = []
        self._bot = BoxesElement(None)
    # Private methods
        
    def _union(self, tuple1, tuple2):
        (l1, r1) = tuple1
        (l2, r2) = tuple2
        return (min(l1, l2), max(r1, r2))
        
    def _intersect(self, tuple1, tuple2):
        (l1, r1) = tuple1
        (l2, r2) = tuple2
        if r1 < l1 or r2 < l2:
            return None
        return (max(l1, l2), min(r1, r2))
        
    def _interval(self, element, variable):
        if element.ranges is None:
            return None
        if variable in element.ranges:
            return element.ranges[variable]
        else:
            return self.variables[variable]

    def _normalize(self, element):
        if element.ranges is None:
            return self._bot
        result = self._copy(element)
        for variable in element.ranges:
            if element.ranges[variable] == self.variables[variable]:
                del result.ranges[variable]
        return result

    def _copy(self, element):
        if element.ranges is None:
            return self._bot
        result = BoxesElement({})
        for variable in element.ranges:
            result.ranges[variable] = element.ranges[variable]
        return result

    def _is_literal(self, value):
        return isinstance(value, numbers.Number) 

    def _op_binary_intervals(self,
                            element,
                            operator,
                            target_var,
                            interval1,
                            interval2):
        if element.ranges is None:
            return self._bot
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
                return self._bot
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
            result.ranges[target_var] = (cl, cr)
        else:
            result.ranges[target_var] = self.variables[target_var]
        return self._normalize(result)
        
    # Variable handling

    def add_integer_var(self, variable, min_val, max_val):
        self.variables[variable] = (min_val, max_val)

    def add_bool_var(self, variable):
        self.add_integer_var(variable, 0, 1)
        
    # I/O

    def to_string(self, element):
        if element.ranges is None:
            return '<BOT>'
        elif len(element.ranges) == 0:
            return '<TOP>'
        result = '['
        keys_sorted = sorted(element.ranges.keys())
        for variable in keys_sorted:
            result += ('%s in [%s, %s], '
                       % (variable,
                          element.ranges[variable][0],
                          element.ranges[variable][1]))
        if result.endswith(', '):
            result = result[:-2]
        result += ']'
        return result

    # Algebraic operations
    
    def get_top(self):
        return BoxesElement({})

    def get_bot(self):
        return self._bot

    def add_constant(self, constant):
        self.constants.append(constant)
        self.constants = sorted(self.constants)
    
    def is_subseteq(self, element1, element2):
        if element1.ranges is None:
            return True
        if element2.ranges is None:
            return False
        for variable in element2.ranges:
            (l2, r2) = element2.ranges[variable]
            if variable in element1.ranges:
                (l1, r1) = element1.ranges[variable]
                if not (l2 <= l1 and r2 >= r1):
                    return False
        return True

    def is_eq(self, element1, element2):
        return (self.is_subseteq(element1, element2)
                and self.is_subseteq(element2, element1))

    def union(self, element1, element2):
        result = BoxesElement({})
        if element1.ranges is None:
            return self._copy(element2)
        elif element2.ranges is None:
            return self._copy(element1)
        for variable in element1.ranges:
            if variable in element2.ranges:
                result.ranges[variable] \
                    = self._union(self._interval(element1, variable),
                                  self._interval(element2, variable))
        # if a variable is set in element2, it'll be
        # full range anyway in element2
        return self._normalize(result)

    def intersect(self, element1, element2):
        if element1.ranges is None:
            return self._bot
        elif element2.ranges is None:
            return self._bot
        result = BoxesElement({})
        for variable in element1.ranges:
            result.ranges[variable] = element1.ranges[variable]
        for variable in element2.ranges:
            result.ranges[variable] \
                = self._intersect(self._interval(result, variable),
                                  self._interval(element2, variable))
            if result.ranges[variable] is None:
                return self._bot
        return result

    def widen(self, element1, element2):
        result = self._copy(element2)
        if element1.ranges is None or element2.ranges is None:
            return self._copy(element2)
        for variable in element1.ranges:
            (l1, r1) = self._interval(element1, variable)
            (l2, r2) = self._interval(element2, variable)
            l = l2
            r = r2
            v_min, v_max = self.variables[variable]
            
            if (l1 > l2):
                matching_constant = None
                for constant in self.constants:
                    if constant <= l2:
                        if (matching_constant is None or
                            matching_constant < constant):
                            matching_constant = constant
                    # TODO: int ranges
                if matching_constant:
                    l = matching_constant
                else: 
                    l = v_min
            if (r2 > r1):
                matching_constant = None
                for constant in self.constants:
                    if constant >= r2:
                        if (matching_constant is None or
                            matching_constant > constant):
                            matching_constant = constant
                    # TODO: ranges
                if matching_constant:
                    r = matching_constant
                else: 
                    r = v_max
            result.ranges[variable] = (l, r)
        return self._normalize(result)

    # Semantics of the abstract machine
    
    def op_load_constant(self, element, target_var, constant):
        if element.ranges is None:
            return self._bot
        result = self._copy(element)
        # TODO: what if constant not in range(variable)?
        result.ranges[target_var] = (constant, constant)
        return self._normalize(result)

    def op_load_variable(self, element, target_var, source_var):
        if element.ranges is None:
            return self._bot
        result = self._copy(element)
        # TODO: what if constant not in range(variable)?
        if source_var in result.ranges:
            result.ranges[target_var] = element.ranges[source_var]
        else:
            del result.ranges[target_var] # no info for source_var
        return self._normalize(result)
    
    def op_binary(self,
                  element,
                  operator,
                  target_var,
                  op1,
                  op2):
        if element.ranges is None:
            return self._bot
        if self._is_literal(op1):
            i1 = (op1, op1)
        else:
            i1 = self._interval(element, op1) 
        if self._is_literal(op2):
            i2 = (op2, op2)
        else:
            i2 = self._interval(element, op2)
        return self._op_binary_intervals(element,
                                         operator,
                                         target_var,
                                         i1,
                                         i2)
    
    def cond_binary(self,
                    element,
                    operator,
                    op1,
                    op2):
        if element.ranges is None:
            return self._bot
        if operator == '>' :
            return self.cond_binary(element, '<', op2, op1)
        elif operator == '>=' :
            return self.cond_binary(element, '<=', op2, op1)
        result = self._copy(element)
        i1 = None
        i2 = None
        left_var = None
        right_var = None
        if self._is_literal(op1):
            i1 = (op1, op1)
        else:
            i1 = self._interval(element, op1)
            left_var = op1
        if self._is_literal(op2):
            i2 = (op2, op2)
        else:
            i2 = self._interval(element, op2)
            right_var = op2
        (l1, r1) = i1
        (l2, r2) = i2
        if operator == '==':
            buffer = self._intersect((l1, r1), (l2, r2))
            if buffer is None:
                return self._bot
        elif operator == '!=':
            if op1 == op2:
                return self._bot
            if (l1 - r1) == 0 and (l2-r2) == 0 and (l1 == l2):
                return None
        new_i1 = None
        new_i2 = None
        if operator == '<=':
            if r2 < l1:
                return self._bot
            new_i1 = (l1, min(r1, r2))        
            new_i2 = (max(l1, l2), r2)
        elif operator == '<':
            if op1 == op2:
                return self._bot
            if r2 <= l1:
                return self._bot
            new_i1 = (l1, min(r1, r2-1))        
            new_i2 = (max(l1+1, l2), r2)
        else:
            print 'Unknown operator: %s ' % operator
        if new_i1 and left_var:
            result.ranges[left_var] = new_i1
        if new_i2 and right_var:
            result.ranges[right_var] = new_i2
        return self._normalize(result)

    def project_var(self, element, variable):
        result = self._copy(element)
        if result.ranges is None:
            return self._bot
        if variable in result.ranges:
            del result.ranges[variable]
        return result
    
