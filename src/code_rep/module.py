##############################
#
# module.py 
#
# Module
# (collection of methods)
#
# (C) 2016, Andreas Gaiser
##############################

import method
import variable

class Module(object):
    ''' A collection of methods. '''

    def __init__(self, id):
        self.id = id
        self._methods = set()
        self._variables = {}
        self._outs = {}
        self._ins = {}
        self._in_invocations = {}
        self._out_invocations = {}
        self.initial = None
        self.final = None

    def create_invocation(self,
                          invoking_method,
                          invoked_method,
                          argument_vars,
                          target_var):
        assert invoking_method in self._methods
        assert invoked_method in self._methods
        result = method.Invocation(invoking_method,
                                   invoked_method,
                                   argument_vars,
                                   target_var)
        self._in_invocations.setdefault(invoked_method, []).append(result)
        self._out_invocations.setdefault(invoking_method, []).append(result)
        self.add_edge(invoking_method, invoked_method)
        self.add_edge(invoked_method, invoking_method)
        
        return result
        
    def add_method(self, new_method,
                   is_init=False, is_final=False):
        assert isinstance(new_method, method.Method)
        self._methods.add(new_method)
        self._outs[new_method] = set()
        self._ins[new_method] = set()
        self._in_invocations[new_method] = []
        self._out_invocations[new_method] = []
        if is_init:
            self.initial = new_method
        if is_final:
            self.final = new_method

    def add_edge(self, from_method, to_method):
        self._outs[from_method].add(to_method)
        self._ins[to_method].add(from_method)

    def invocations_with_invoked(self, method):
        return self._in_invocations[method]
    
    def invocations_with_invoking(self, method):
        return self._out_invocations[method]
        
    def successors(self, method):
        ''' Return all direct successor methods of method. '''
        try:
            return self._outs[method]
        except:
            return set()

    def predecessors(self, method):
        ''' Return all direct predecessor methods of method. '''
        try:
            return self._ins[method]
        except:
            return set()
        
    def create_variable(self, id, type):
        v = variable.ModuleVariable(id, type, self)
        self._variables[id] = v
        return v

    def get_variable(self, id):
        try:
            return self._variables[id]
        except:
            return None
        
    def callgraph_to_string(self):
        result = ''
        for m1 in self._methods:
            for m2 in self.successors(m1):
                result += '%s -> %s \n' % (m1.id, m2.id)
        return result
    
    def methods(self):
        return self._methods
    
    def __str__(self):
        result = 'Module %s:\n' % self.id
        for m in self._methods:
            result += '%s\n' % m.id
        return result
    
