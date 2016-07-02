##############################
#
# method.py 
#
# Method control flow graph
#
# (C) 2016, Andreas Gaiser
##############################

import instr

class Invocation(object):
    ''' An invocation of another method. '''

    def __init__(self,
                 invoking_method,
                 invoked_method,
                 argument_vars,
                 target_var):
        self.arguments = argument_vars
        self.invoking_method = invoking_method
        self.invoked_method = invoked_method
        self.target_var = target_var

    def __str__(self):
        result = 'call %s::%s(%s): %s' % (self.invoked_method.module.id,
                                          self.invoked_method.id,
                                      ', '.join(map(lambda v: '%s' % v,
                                                    self.arguments)),
                                      self.target_var)
        return result    

    @staticmethod
    def perform_return(self, element, dom):
        ''' Performs a return to the invoker. '''
        # ABI: 
        # perform an assignment if target_var is specified
        pass
        
    @staticmethod
    def perform_invoke(element, dom):
        ''' Performs the effects of an invocation. '''
        pass
                    
     
class BasicBlock(object):
    ''' A basic block within a method CFG. Contains a sequence
    of instructions and a unique id.'''
    
    def __init__(self, id):
        self.id = id
        self._instructions = []
        self._parent = None # set by block
        
    def __str__(self):
        result = 'BasicBlock(%s)[ ' % self.id
        for instruction in self.instructions():
            result += '%s; ' % instruction
        result += ' ]'
        return result

    def instructions(self):
        return self._instructions

    def append_instruction(self, instruction):
        self._instructions.append(instruction)

    def set_parent(self, parent):
        self._parent = parent

    def get_parent(self):
        return self._parent
    
    
class FlowEdge(object):

    def __init__(self, condition, invocation):
        self.condition = condition
        self.invocation = invocation

    def __str__(self):
        return 'EDGE:%s-%s' % (self.condition, self.invocation)

    
class Method(object):
    
    def __init__(self, id, module):
        ''' Create a method CFG. id denotes the actual method, module
        the containing module object. Creates an empty initial and an empty
        final block automatically. '''
        self.id = id
        self.module = module
        if module:
            module.add_method(self)
        self._blocks = []
        self._edges = {}
        self._outs = {}
        self._ins = {}
        self._invocations = []
        self._variables = {}
        init_block = BasicBlock('__initial')
        final_block = BasicBlock('__final')
        self.add_block(init_block)
        self.add_block(final_block)
        self.initial = init_block
        self.final = final_block
        self._parameters = []
        self.return_variable = None
        self._local_variables = []
        
    def __str__(self):
        return self.id
        result = '%s::%s:\n' % (self.module.id, self.id)
        result += 'Parameter: '
        for parameter in self._parameters:
            result += '%s ' % parameter
        result += '\n'
        result += 'Return value: %s\n' % self.return_variable
        for (s, t) in self._edges:
            condition = self._edges[(s, t)].condition
            invocation = self._edges[(s, t)].invocation
            result += ('%s ==((%s, %s))==> %s \n'
                       % (s, condition, invocation, t))
        return result 
    
    def add_block(self, block):
        ''' Add a basic block. '''
        self._blocks.append(block)
        self._outs[block] = []
        self._ins[block] = []
        block.set_parent(self)
        
    def add_blocks(self, *blocks):
        ''' Add a sequence of basic blocks. '''
        for block in blocks:
            self.add_block(block)

    def blocks(self):
        ''' Get a list of all basic blocks. '''
        return self._blocks
            
    def set_edge(self, from_block, to_block,
                 condition=None, invocation=None):
        ''' Insert an edge between from_block and to_block, with
        an optional condition and an optional invocation '''
        edge = FlowEdge(condition, invocation)
        assert from_block in self._blocks
        assert to_block in self._blocks
        self._edges[(from_block, to_block)] = edge
        self._outs[from_block].append(to_block)
        self._ins[to_block].append(from_block)
        if invocation:
            self._invocations.append(invocation)
            
    def get_edge(self, from_block, to_block):
        try:
            return self._edges[(from_block, to_block)]
        except:
            return None
        
    def successors(self, block):
        ''' Return all direct successor blocks of block. '''
        assert block in self._blocks
        return self._outs[block]

    def predecessors(self, block):
        ''' Return all direct predecessor blocks of block. '''
        assert block in self._blocks
        return self._ins[block]

    def add_local_variable(self, v):
        self._local_variables.append(v)
        v.set_parent(self)
        return v

    def add_parameter(self, v):
        self._parameters.append(v)
        v.set_parent(self)
        return v

    def set_return_variable(self, v):
        self.return_variable = v
    
    def get_variable(self, id):
        try:
            return self._variables[id]
        except:
            return None

    def parameters(self):
        return self._parameters
    
    def local_variables(self):
        return self._local_variables 

    def allocations(self):
        result = []
        for block in self._blocks:
            for instruction in block.instructions():
                if isinstance(instruction, instr.Alloc):
                    result.append(instruction)
        return result
