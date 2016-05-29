##############################
#
# eval.py 
# 
# Compute Evaluation sequences
#
# (C) 2016, Andreas Gaiser
##############################


class EvalSequence(object):
    ''' Stores a possibly nested sequence of basic blocks. '''

    _counter = 0
    
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

    @staticmethod
    def compute_bourdoncle_sequence(method_or_module, reverse=False):
        ''' Compute an evaluation sequence according to Bourdoncle. '''
        dfn = {}
        partition = EvalSequence([])
        EvalSequence._counter = 0
        stack = []
            
        def component(vertex):
            p = EvalSequence([])
            outgoings = (method_or_module.successors(vertex)
                         if not reverse
                         else method_or_module.predecessors(vertex))
            for succ in outgoings:
                if dfn.setdefault(succ, 0) == 0:
                    visit(succ, p)
            p.push_first(vertex)
            return p
            
        def visit(loc, p):
            stack.append(loc)
            EvalSequence._counter += 1
            head = EvalSequence._counter
            dfn[loc] = EvalSequence._counter
            loop = False
            outgoings = (method_or_module.successors(loc)
                         if not reverse
                         else method_or_module.predecessors(loc))
            for succ in outgoings:
                if dfn.setdefault(succ, 0) == 0:
                    min = visit(succ, p)
                else:
                    min = dfn.setdefault(succ, 0)
                if min <= head and min != -1:
                    head = min
                    loop = True
            if head == dfn.setdefault(loc, 0):
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
            visit(method_or_module.final, partition)
        else:
            visit(method_or_module.initial, partition)
        return partition
    
