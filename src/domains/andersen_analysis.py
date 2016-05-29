##############################
#
# andersen_analysis.py 
#
# Andersen pointer analysis
#
# (C) 2016, Andreas Gaiser
##############################

from z3 import *

def generate_constraints(method_cfg):
    # Andersen is context-insensitive
    # and flow-insensitive aff
    # Andersen rules
    # Relation
    points_to = Function('points_to', IntSort(), IntSort(), BoolSort())
    assign = Function('points_to', IntSort(), IntSort(), BoolSort())
    
    s = Fixedpoint()
    x = Var(0, IntSort())
    y = Var(1, IntSort())
    
    s.register_relation(points_to)
    s.rule(points_to(0, 1))
    s.rule(assign(2, 1))
    s.rule(points_to(x, y), assign(x, y))
    # L1: x0 := &x1
    #     x2 := x1
    print s.query(points_to(2, 1))
    pass

if __name__ == '__main__':
    generate_constraints(None)
    
