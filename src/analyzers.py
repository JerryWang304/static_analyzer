##############################
#
# analyzer.py 
# 
# interprocedural analyzer.
#
# (C) 2016, Andreas Gaiser
##############################

from analysis.eval import *
from code_rep.instr import *
from code_rep.variable import *
from code_rep.type_system import *
            
class MethodAnalyzer(object):

    def _add_var(self, v):
        arg_type = v.type
        if isinstance(arg_type, Integer):
            if arg_type.is_bool_type():
                self._dom.add_bool_var(v)
            else:
                self._dom.add_integer_var(v,
                                          arg_type.min_value,
                                          arg_type.max_value)

    
    def __init__(self, method, dom, module_analyzer=None):
        self._method = method
        self._dom = dom
        self._module_analyzer = module_analyzer
        self._forward_sequence = EvalSequence.compute_bourdoncle_sequence(
            method_or_module=method,
            reverse=False)
        self._backward_sequence = EvalSequence.compute_bourdoncle_sequence(
            method_or_module=method,
            reverse=True)
        self.in_values, self.out_values = {}, {}
        # add all variables
        for parameter in method.parameters:
            self._add_var(parameter)
        if method.return_variable:
            self._add_var(method.return_variable)
        for v in method.local_variables():
            self._add_var(v)

    def get_final_out_value(self):
        return self.out_values[self._method.final]
            
    def analyze(self,
                head_init_element,
                ordinary_init_element,
                analyze_forward = True,
                iterations_without_widening = 5):
        ins, outs = {}, {}
        head = (self._method.initial
                if analyze_forward
                else self._method.final)
        sequence = (self._forward_sequence
                    if analyze_forward
                    else self._backward_sequence)
        for loc in self._method.blocks():
            if analyze_forward:
                ins[loc] = (head_init_element
                            if loc == head
                            else ordinary_init_element)
                outs[loc] = ordinary_init_element
            else:
                outs[loc] = (head_init_element
                             if loc == head
                             else ordinary_init_element)
                ins[loc] = ordinary_init_element
                
        # TODO: make this more extensible!
        def apply_instruction(instruction, value):

            def apply_direct_assignment():
                target = instruction.target
                rhs = instruction.rhs
                # case distinction:
                if len(rhs) == 1:
                    # constant or variable
                    op1 = rhs[0]
                    return self._dom.op_binary(value,
                                               '+',
                                               target,
                                               op1,
                                               0)
                elif len(rhs) == 3:
                    (operator, op1, op2) = rhs
                    return self._dom.op_binary(value,
                                               operator,
                                               target,
                                               op1,
                                               op2)

            if isinstance(instruction, DirectAssignment):
                return apply_direct_assignment()
            elif isinstance(instruction, Alloc):
                pass #TODO
            elif isinstance(instruction, Load):
                pass #TODO
            elif isinstance(instruction, Store):
                pass #TODO
            elif isinstance(instruction, Address):
                pass #TODO
            else:
                pass #TODO
            return value
                
        def _apply_condition(condition, value):
            (operator, op1, op2) = condition
            return self._dom.cond_binary(value,
                                         operator,
                                         op1,
                                         op2)

        def stabilize(component):
            widen_count = 0
            elements = component.get_sequence()
            widen_loc = None
            if (len(elements) > 0
                and not isinstance(elements[0], EvalSequence)):
                widen_loc = elements[0]
            decreasing = False
            while not decreasing:
                decreasing = True
                for element in elements:
                    print "Processing: %s" % element
                    if isinstance(element, EvalSequence):
                        stabilize(element)
                    else:
                        new_input = (ins[element]
                                     if analyze_forward
                                     else outs[element])
                        # single element
                        edges = (self._method.predecessors(element)
                                 if analyze_forward
                                 else self._method.successors(element))
                        for neighbour in edges:
                            current_edge\
                                = (self._method.get_edge(neighbour,
                                                         element)
                                   if analyze_forward
                                   else _method.get_edge(element,
                                                         neighbour))
                                     # is there an invocation?
                            invocation = current_edge.invocation
                            neighbour_element = (outs[neighbour]
                                                 if analyze_forward
                                                 else ins[neighbour])
                            if invocation and self._module_analyzer:
                                # first: propagate inputs
                                self._module_analyzer.perform_call(invocation,
                                                                   neighbour_element)
                                # get the return value
                                new_input = self._dom.union(
                                    new_input,
                                    self._module_analyzer.perform_return(
                                        invocation=invocation))
                                continue
                            # else: is there a condition?
                            condition = current_edge.condition
                            new_input = self._dom.union(
                                new_input,
                                (_apply_condition(
                                    condition,
                                    neighbour_element)
                                 if (condition is not None)
                                 else neighbour_element))
                        new_output = new_input
                        if analyze_forward:
                            for instruction in element.instructions:
                                new_output = apply_instruction(
                                    instruction,
                                    new_output)
                        else:
                            for instruction in reversed(element.instructions):
                                new_output = apply_instruction(
                                    instruction,
                                    new_output)
                        old_element = (outs[element]
                                       if analyze_forward
                                       else ins[element])
                        if element == widen_loc:
                            if widen_count >= iterations_without_widening:
                                new_output = self._dom.widen(old_element,
                                                             new_output)
                            else:
                                widen_count += 1
                        decreasing = self._dom.is_subseteq(
                            new_output,
                            old_element)
                        if analyze_forward:
                            outs[element] = new_output
                            ins[element] = new_input
                        else:
                            ins[element] = new_output
                            outs[element] = new_input
                            
        stabilize(sequence)
        #return ins, outs
        self.in_values = ins
        self.out_values = outs


class Module0CFAForwardAnalyzer(object):

    def __init__(self, module, dom):
        self._module = module
        self._dom = dom
        self._forward_sequence\
            = EvalSequence.compute_bourdoncle_sequence(
                method_or_module=module,
                reverse=False)
        self._backward_sequence\
            = EvalSequence.compute_bourdoncle_sequence(
                method_or_module=module,
                reverse=True)
        self.outs = {}
        self._invocation_ins, self._invocation_outs = {}, {}
        
    def perform_return(self,
                       invocation):
        ''' Transform the element by assigning the return variable of
        the invoking method to the corresponding value in element, and
        possibly project local variables. '''
        invoker = invocation.invoking_method
        invoked = invocation.invoked_method
        element = self.outs[invoked]
        if invoked.return_variable and invocation.target_var:
            # TODO: type check
            # TODO: direct assignment in dom
            element = self._dom.op_binary(element,
                                          '+',
                                          invocation.target_var,
                                          invoked.return_variable,
                                          0)
        # remove vars of the invoked
        for var in invoked.parameters:
            element = self._dom.project_var(element, var)
        for var in invoked.local_variables():
            element = self._dom.project_var(element, var)
        self._invocation_outs[invocation] = element
        return element

    def perform_call(self,
                     invocation,
                     element):
        ''' Transform the element by assigning the arguments to
        the parameter variables and projecting away all others.
        ALSO UPDATES THE INVOCATION ELEMENT'''
        invoker = invocation.invoking_method
        invoked = invocation.invoked_method
        index = 0
        for (arg, parameter) in zip(invocation.arguments, invoked.parameters):
            element = self._dom.op_load_variable(element,
                                                 parameter,
                                                 arg)
        # remove vars of the invoker
        for var in invoker.parameters:
            element = self._dom.project_var(element, var)
        for var in invoker.local_variables():
            element = self._dom.project_var(element, var)
        self._invocation_ins[invocation] = element
            
    def analyze(self,
                head_init_element,
                ordinary_init_element,
                iterations_without_widening = 5):
        head = self._module.initial
        sequence = self._forward_sequence
        # create method analyzers
        # and initial input values
        analyzers = {}       
        for inner_method in self._module.methods():
            analyzers[inner_method] = MethodAnalyzer(
                inner_method,
                self._dom,
                self)
            self.outs[inner_method] = ordinary_init_element
            for invocation in self._module.invocations_with_invoked(inner_method):
                self._invocation_ins[invocation] = ordinary_init_element
                self._invocation_outs[invocation] = ordinary_init_element
                            
        def stabilize_forward(component):
            widen_count = 0
            computation_sequence = component.get_sequence()
            widen_loc = None
            if (len(computation_sequence) > 0
                and not isinstance(computation_sequence[0], EvalSequence)):
                widen_loc = computation_sequence[0]
            decreasing = False
            while not decreasing:
                decreasing = True
                for computation_element in computation_sequence:
                    if isinstance(computation_element, EvalSequence):
                        stabilize_forward(computation_element)
                        continue
                    method = computation_element
                    # create new input
                    new_input = (head_init_element
                                 if method == head
                                 else ordinary_init_element)
                    # single element
                    invoked_invocations\
                        = self._module.invocations_with_invoked(method)
                    for invocation in invoked_invocations:
                        new_input = self._dom.union\
                                    (new_input,
                                     self._invocation_ins[invocation])
                    # analyze
                    analyzers[method].analyze(new_input,
                                              ordinary_init_element,
                                              True,
                                              iterations_without_widening)
                    # TODO: use old values of method analyzer
                    old_output = self.outs[method]
                    new_output = analyzers[method].get_final_out_value()
                    if method == widen_loc:
                        if widen_count >= iterations_without_widening:
                            new_output = self._dom.widen(old_output,
                                                         new_output)
                        else:
                            widen_count += 1
                    decreasing = self._dom.is_subseteq(
                        new_output,
                        old_output)
                    self.outs[method] = new_output
                            
        stabilize_forward(sequence)
        for out in self.outs:
            print "OUT VALUE FOR %s: %s" % (out, self._dom.to_string(self.outs[out]))
        return self.outs
