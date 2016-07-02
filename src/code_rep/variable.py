##############################
#
# variable.py 
#
# Variables
#
# (C) 2016, Andreas Gaiser
##############################


class Variable(object):

    def __init__(self, id, type, parent=None):
        self.id = id
        self._type = type
        self._parent = parent

    def set_parent(self, parent):
        self._parent = parent
        
    def __str__(self):
        return '%s(parent:%s)' % (self.id, self._parent)

    def set_parent(self, parent):
        self._parent = parent

    def get_parent(self):
        return self._parent

    def get_type(self):
        return self._type
