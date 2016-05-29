##############################
#
# instr.py 
#
# Instructions in basic blocks
# and related classes.
#
# (C) 2016, Andreas Gaiser
##############################

class Assignment(object):
    ''' Abstract assignment class '''
    
    def __init__(self):
        pass

    
class DirectAssignment(Assignment):
    ''' Direct assigment 'target_object = rhs'. '''
    
    def __init__(self, target_object, rhs):
        super(Assignment, self).__init__()
        self.target = target_object
        self.rhs = rhs

    def __str__(self):
        return '%s := %s' % (self.target, self.rhs)
    

class Alloc(Assignment):
    ''' Allocate element on the heap: 
    target_object = new alloc_type(size_var). '''

    def __init__(self, target_object, alloc_type, size_var):
        super(Assignment, self).__init__()
        self.target = target_object
        self.alloc_type = alloc_type#
        self.rhs = size_var

    def __str__(self):
        return '%s := new %s(%s)' % (self.target,
                                     self.alloc_type,
                                     self.rhs)

    
class Load(Assignment):
    ''' Indirect assignment: target_object = *(rhs) '''

    def __init__(self, target_object, rhs):
        super(Assignment, self).__init__()
        self.target = target_object
        self.rhs = rhs

    def __str__(self):
        return '%s := *%s' % (self.target, self.rhs)


class Store(Assignment):
    ''' Indirect assignment: *target_object = rhs. '''

    def __init__(self, target_object, rhs):
        super(Assignment, self).__init__()
        self.target = target_object
        self.rhs = rhs

    def __str__(self):
        return '*%s := %s' % (self.target, self.rhs)

    
class Address(Assignment):
    ''' Address-taking assignment: target_object = &rhs '''

    def __init__(self, target_object, rhs):
        super(Assignment, self).__init__()
        self.target = target_object
        self.rhs = rhs

    def __str__(self):
        return '%s := &%s' % (self.target, self.rhs)


