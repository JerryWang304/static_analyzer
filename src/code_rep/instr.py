##############################
#
# instr.py 
#
# Instructions in basic blocks
# and related classes.
#
# (C) 2016, Andreas Gaiser
##############################

import variable
import numbers

class Assignment(object):
    ''' Abstract assignment class '''
    
    def __init__(self, target):
        assert isinstance(target, variable.Variable)
        self.target = target

    
class DirectVariableAssignment(Assignment):
    ''' Direct assignment 'target = source'. source are variables. '''
    
    def __init__(self, target, source):
        assert isinstance(source, variable.Variable)
        super(DirectVariableAssignment, self).__init__(target)
        self.source = source

    def __str__(self):
        return '%s := %s' % (self.target, self.source)

    
class ConstantAssignment(Assignment):
    ''' Direct assignment 'target_object = source'. source is a literal.'''
    
    def __init__(self, target, source):
        assert isinstance(source, numbers.Number) # or string? 
        super(ConstantAssignment, self).__init__(target)
        self.source = source

    def __str__(self):
        return '%s := %s' % (self.target, self.source)

    
class BinaryOpAssignment(Assignment):
    ''' Binary assigment 'target_object = operand1 operator operand2'.'''
    
    def __init__(self, target, operator, operand1, operand2):
        super(BinaryOpAssignment, self).__init__(target)
        assert operator in ['+', '-', '*', '%', '/']
        assert (operand1 in variable.Variable)
        assert (operand2 in variable.Variable)
        self.operand1 = operand1
        self.operand2 = operand2
        self.operator = operator 

    def __str__(self):
        return '%s := %s %s %s' % (self.target,
                                   self.operand1,
                                   self.operator,
                                   self.operand2)

    
class UnaryOpAssignment(Assignment):

    ''' Unary assignment 'target_object = operator operand1'.'''
    
    def __init__(self, target, operator, operand):
        super(UnaryOpAssignment, self).__init__(target)
        self.operand = operand
        self.operator = operator 

    def __str__(self):
        return '%s := %s %s' % (self.target, self.operator, self.operand)
    
    
class Alloc(Assignment):
    ''' Allocate element on the heap: target_object = new alloc_type(size_var). '''

    def __init__(self, target, alloc_type, size_var):
        super(Alloc, self).__init__(target)
        self.alloc_type = alloc_type
        self.rhs = size_var

    def __str__(self):
        return '%s := new %s(%s)' % (self.target,
                                     self.alloc_type,
                                     self.rhs)

    
class Load(Assignment):
    ''' Indirect assignment: target_object = *(rhs) '''

    def __init__(self, target, rhs):
        super(Load, self).__init__(target)
        self.rhs = rhs

    def __str__(self):
        return '%s := *%s' % (self.target, self.rhs)


class Store(Assignment):
    ''' Indirect assignment: *target_object = rhs. '''

    def __init__(self, target, rhs):
        super(Store, self).__init__(target)
        self.rhs = rhs

    def __str__(self):
        return '*%s := %s' % (self.target, self.rhs)

    
class Address(Assignment):
    ''' Address-taking assignment: target_object = &rhs '''

    def __init__(self, target, rhs):
        super(Address, self).__init__(target)
        self.rhs = rhs

    def __str__(self):
        return '%s := &%s' % (self.target, self.rhs)

