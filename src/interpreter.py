##############################
#
# interpreter.py 
#
# Actual interpreter
#
# (C) 2016, Andreas Gaiser
##############################


class ComputationComponent(object):

    def __init__(self, sequence):
        self._sequence = sequence

    def push_first(self, element):
        self._sequence.insert(0, element)

    def __str__(self):
        result = '['
        for obj in self._sequence:
            result += '%s ' % obj
        result += ']'
        return result

    def get_sequence(self):
        return self._sequence

    
class Assignment(object):

    def __init__(self, target_object, rhs):
        self.target = target_object
        self.rhs = rhs

    def __str__(self):
        return '%s := %s' % (self.target, self.rhs)
    
class BasicBlock(object):

    def __init__(self, id, assignments):
        self.id = id
        self.assignments = assignments

    def __str__(self):
        result = 'BasicBlock(%s)[ ' % self.id
        for assignment in self.assignments:
            result += '%s;' % assignment
        result += ' ]'
        return result
        
class FlowEdge(object):

    def __init__(self, label):
        self.label = label

    def __str__(self):
        return 'EDGE:%s' % self.label
    
class MethodCFG(object):
    
    def __init__(self, init_location, end_location):
        self.control_locs = [init_location, end_location]
        self.init_loc = init_location
        self.end_loc = end_location
        self.widen_points = []
        self.edges = {}
        self.out_edges = {}
        self.in_edges = {}
        self.counter = 0
        self.in_values = {}
        self.out_values = {}
        self.add_block(init_location)
        self.add_block(end_location)
        
    def __str__(self):
        result = ''
        for (s, t) in self.edges:
            condition = self.edges[(s, t)].label
            result += '%s ==((%s))==> %s \n' % (s, condition, t)
        return result 

    def compute_bourdoncle_widenpoints(self, reverse=False):
        dfn = {}
        partition = ComputationComponent([])
        self.counter = 0
        stack = []
        for node in self.control_locs:
            dfn[node] = 0
            
        def component(vertex):
            p = ComputationComponent([])
            outgoings = (self.out_edges[vertex]
                         if not reverse else self.in_edges[vertex])
            for succ in outgoings:
                if dfn[succ] == 0:
                    visit(succ, p)
            p.push_first(vertex)
            return p
            
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
                    p.push_first(component(loc))
                else:
                    p.push_first(loc)
            return head
        if reverse:
            visit(self.end_loc, partition)
        else:
            visit(self.init_loc, partition)
        return partition
    
    def add_block(self, control_loc, is_widen_point = False):
        self.control_locs.append(control_loc)
        if is_widen_point:
            self.widen_points.append(control_loc)
        self.out_edges[control_loc] = []
        self.in_edges[control_loc] = []
            
    def set_edge(self, loc1, loc2, condition):
        edge = FlowEdge(condition)
        assert loc1 in self.control_locs
        assert loc2 in self.control_locs
        self.edges[(loc1, loc2)] = edge
        self.out_edges.setdefault(loc1, []).append(loc2)
        self.in_edges.setdefault(loc2, []).append(loc1)
       
    def prepare(self):
        self.forward_computation_sequence = self.compute_bourdoncle_widenpoints(reverse=False)
        self.backward_computation_sequence = self.compute_bourdoncle_widenpoints(reverse=True)

    # evaluate an assignment
    # TODO: make this more extensible!
    def _apply_assignment(assignment, value):
        target = assignment.target
        rhs = assignment.rhs
        # case distinction:
        if len(rhs) == 1:
            # constant or variable
            op1 = rhs[0]
            return dom.op_binary(value,
                                 '+',
                                 target,
                                 op1,
                                 0)
        elif len(rhs) == 3:
            (operator, op1, op2) = rhs
            return dom.op_binary(value,
                                 operator,
                                 target,
                                 op1,
                                 op2)

    def _apply_condition(condition, value):
        (operator, op1, op2) = condition
        return dom.cond_binary(value,
                               operator,
                               op1,
                               op2)
        
    def forward(self,
                dom,
                head_init_element,
                ordinary_init_element,
                iterations_without_widening = 5):
        ins = {}
        outs = {}
        for loc in self.control_locs:
            ins[loc] = head_init_element if loc == self.init_loc else ordinary_init_element
            outs[loc] = ordinary_init_element

        def stabilize(component):
            elements = component.get_sequence()
            widen_loc = None
            if (len(elements) > 0
                and not isinstance(elements[0], ComputationComponent)):
                widen_loc = elements[0]
            decreasing = False
            while not decreasing:
                decreasing = True
                for element in elements:
                    if isinstance(element, ComputationComponent):
                        stabilize(element)
                    else:
                        new_input = ins[element]
                        # single element
                        for source in self.in_edges[element]:
                            current_edge = self.edges[(source, element)]
                            # is there a condition?
                            condition = current_edge.label
                            new_input = dom.union(new_input,
                                               (self._apply_condition(condition, outs[source])
                                                if (condition is not None) else outs[source]))
                        # compute output                  
                        new_output = new_input
                        for assignment in assignments:
                            new_output = apply_assignment(assignment,  new_output)
                        if element == widen_loc:
                            new_output = dom.widen(outs[element], new_output)
                        decreasing = dom.is_subseteq(new_output, outs[element])
                        outs[element] = new_output
                        ins[element] = new_input

        stabilize(self.forward_computation_sequence)
        self.in_values = ins
        self.out_values = outs


if __name__ == '__main__':


    a1 = Assignment('x', [2])
    a2 = Assignment('y', ['+', 'y', 2])
    a3 = Assignment('x', ['+', 'x', 1])
    a4 = Assignment('c', ['<', 'y', 'x'])
    a5 = Assignment('d', ['==', 'y', 2])

    b1 = BasicBlock(1, [a1, a2])
    b2 = BasicBlock(2, [a3, a4])
    b3 = BasicBlock(3, [a5])
    
    
    cfg = MethodCFG(b1, b3)
    cfg.add_block(b2)
    cfg.set_edge(b1, b2, None)
    cfg.set_edge(b2, b3, ['>=', 'x', 'y'])
    cfg.set_edge(b2, b1, ['<', 'x', 'y'])
    
    print('%s' % cfg)
    cfg.prepare()
    print cfg.forward_computation_sequence
