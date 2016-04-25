##############################
#
# interpreter.py 
#
# Actual interpreter
#
# (C) 2016, Andreas Gaiser
##############################


# (I) Arithmetic expressions
# 
# CONST
# VAR
# VAR (+) CONST
# VAR (+) VAR
#

# given as list-encoded trees.
# e.g.
# X + Y ==> ['+', X, Y]
#
# No nested expressions supported yet.

#
# (II) Assignments
#
# VAR := AExpr
#
# given as list expression:
# X := A + 1 ==> [':=', 'X', ['+', A, 1]]
#
#

#
# (III) Boolean expressions
#
# X (~) Y
# X (~) CONST
#
# given as list expression:
# ['<=', 'x', 'y']


class MethodCFG():

    def __init__(self, init_location, end_location):
        self.control_locs = [init_location, end_location]
        self.init_loc = init_location
        self.end_loc = end_location
        self.widen_points = []
        self.edges = {}
        self.out_edges = {}
        self.in_edges = {}
        self.counter = 0
        
    def to_string(self):
        result = ''
        for (s, t) in self.edges:
            (cond, actions) = self.edges[(s, t)]
            result += '%s -> %s \n\t' % (s, t)
            if cond is None:
                result += ' [True] '
            else:
                result += ' %s ' % cond
            if len(actions) != 0:
                result += '\n\t'
                for action in actions:
                    result += ' @<%s> ' % action
            result += '\n'
            
        return result 
        
    def add_control_loc(self, control_loc, is_widen_point = False):
        self.control_locs.append(control_loc)
        if is_widen_point:
            self.widen_points.append(control_loc)
        self.out_edges[control_loc] = []
        self.in_edges[control_loc] = []
            
    def set_edge(self, loc1, loc2, condition, assignments):
        edge_value = [condition, assignments]
        assert loc1 in self.control_locs
        assert loc2 in self.control_locs
        self.edges[(loc1, loc2)] = edge_value
        self.out_edges.setdefault(loc1, []).append(loc2)
        self.in_edges.setdefault(loc2, []).append(loc1)
       
    def compute_bourdoncle_widenpoints(self, reverse=False):
        dfn = {}
        partition = []
        self.counter = 0
        stack = []
        for node in self.control_locs:
            dfn[node] = 0
            
        def component(vertex):
            p = []
            outgoings = (self.out_edges[vertex]
                         if not reverse else self.in_edges[vertex])
            for succ in outgoings:
                if dfn[succ] == 0:
                    visit(succ, p)
            return [vertex] + p
            
        def visit(loc, p):
            stack.append(loc)
            self.counter += 1
            head = self.counter
            dfn[loc] = self.counter
            loop = False
            outgoings = (self.out_edges[loc]
                         if not reverse else self.in_edges[loc])
            for succ in outgoings:
                if dfn[succ] == 0:
                    min = visit(succ, p)
                else:
                    min = dfn[succ]
                if min <= head and min != -1:
                    head = min
                    loop = True
            if head == dfn[loc]:
                dfn[loc] = -1
                # pop
                element = stack.pop()
                if loop:
                    while element != loc:
                        dfn[element] = 0
                        element = stack.pop()
                    p.insert(0, component(loc))
                else:
                    p.insert(0, loc)
            return head
        if reverse:
            visit(self.end_loc, partition)
        else:
            visit(self.init_loc, partition)
        return partition
        
    def forward_analyze(self,
                        dom,
                        head_init_element,
                        ordinary_init_element,
                        iterations_without_widening = 5):

        # evaluate an assignment
        # TODO: make this more extensible!
        def apply_assignment(assignment, value):
            (variable, expression) = assignment
            # case distinction:
            if len(expression) == 1:
                # constant or variable
                op1 = expression[0]
                return dom.op_binary(value,
                                     '+',
                                     variable,
                                     op1,
                                     0)
            
            elif len(expression) == 3:
                (operator, op1, op2) = expression
                return dom.op_binary(value,
                                     operator,
                                     variable,
                                     op1,
                                     op2)
                

        def apply_condition(condition, value):
            (operator, op1, op2) = condition
            return dom.cond_binary(value,
                                   operator,
                                   op1,
                                   op2)
                
        # init values
        values = {}
        for loc in self.control_locs:
            values[loc] = head_init_element if loc == self.init_loc else ordinary_init_element             
        def iterate(values, do_widen = True):
            new_values = {}
            for loc in values:
                new_values[loc] = values[loc]
            for loc in self.control_locs:
                buffer = values[loc]
                for (s, t) in self.edges:
                    if t == loc:
                        (condition, assignments) = self.edges[(s, t)]
                        # is there a condition?
                        inflow = (apply_condition(condition, values[s])
                                  if (condition is not None) else values[s])
                        for assignment in assignments:
                            inflow = apply_assignment(assignment, inflow)
                        buffer = dom.union(buffer, inflow)
                        
                new_values[loc] = buffer
            if do_widen:
                for loc in self.widen_points:
                    new_values[loc] = dom.widen(values[loc], new_values[loc])
            postfixpoint_reached = True
            for loc in self.control_locs:
                # initialize results
                larger_or_equal = dom.is_subseteq(values[loc], new_values[loc])
                smaller_or_equal = dom.is_subseteq(new_values[loc], values[loc])
                is_increasing = larger_or_equal and not smaller_or_equal
                postfixpoint_reached = postfixpoint_reached and not is_increasing
            return (postfixpoint_reached, new_values)

        postfixpoint_reached = False

        iterations = 0
        while not postfixpoint_reached:
            (postfixpoint_reached, values) \
                = iterate(values,
                          iterations > iterations_without_widening)
            iterations += 1
        print "ITERATIONS: %s" % iterations
        print "**************************"
        for loc in values:
            print('"%s" : "%s"' % (loc, dom.to_string(values[loc])))
            print "**************************"
            
