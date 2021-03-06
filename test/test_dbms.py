import pytest
import dbms


def test_dbms_conditions_intersect_1():
    factory = dbms.DBMFactory(-512, 512)
    factory.add_integer_var(0, 0, 0)
    factory.add_integer_var('x', -512, 512)
    factory.add_integer_var('y', -512, 512)
    factory.add_integer_var('z', -512, 512)
    e1 = factory.get_top()
    e2 = factory.get_top()
    e3 = factory.get_top()
    e4 = factory.get_top()
    # e1: x = y && z > x
    e1 = factory.cond_binary(e1, '==', 'x', 'y')
    e1 = factory.cond_binary(e1, '>', 'z', 'x')
    # e2: z < x
    e2 = factory.cond_binary(e2, '<', 'z', 'x')
    # intersection of e1 and e2 should be empty
    assert factory.is_eq(factory.intersect(e1, e2),
                         factory.get_bot())
    # e3: z == 3
    e3 = factory.cond_binary(e3, '==', 'z', 3)
    assert not factory.is_eq(factory.intersect(e1, e3), factory.get_bot())
    # e4: x == 3
    e4 = factory.cond_binary(e4, '==', 'x', 3)
    e4 = factory.intersect(e1, e4)
    # y should also be 3 now.
    e4_a = factory.cond_binary(e4, '>', 'y', 3)
    e4_b = factory.cond_binary(e4, '<', 'y', 3)
    assert factory.is_eq(e4_a, factory.get_bot())
    assert factory.is_eq(e4_b, factory.get_bot())


def test_dbms_operations_1():
    factory = dbms.DBMFactory(-512, 512)
    factory.add_integer_var(0, 0, 0)
    factory.add_integer_var('x', -512, 512)
    factory.add_integer_var('y', -512, 512)
    factory.add_integer_var('z', -512, 512)
    e1 = factory.get_top()
    e2 = factory.get_top()
    # e1 := x > y
    e1 = factory.cond_binary(e1, '>', 'x', 'y')
    # e1 := e1 and z = x
    e1 = factory.op_binary(e1, '+', 'z', 'x', 0)
    # now: z < y should be impossible
    e2 = factory.cond_binary(e1, '<', 'z', 'y')
    assert factory.is_eq(e2, factory.get_bot())
    
def test_dbms_union_1():
    factory = dbms.DBMFactory(-512, 512)
    factory.add_integer_var(0, 0, 0)
    factory.add_integer_var('x', -512, 512)
    factory.add_integer_var('y', -512, 512)
    # e1 := x == y
    e1 = factory.get_top()
    e1 = factory.cond_binary(e1, '>=', 'x', 6)
    e1 = factory.cond_binary(e1, '<=', 'x', 6)
    # e2 := x == y
    e2 = factory.get_top()
    e2 = factory.cond_binary(e2, '>=', 'x', 6)
    e2 = factory.cond_binary(e2, '<=', 'x', 6)
    e3 = factory.union(e1, e2)
    assert factory.is_eq(e3, e2) 

def test_dbms_assign_1():
    factory = dbms.DBMFactory(-512, 512)
    factory.add_integer_var(0, 0, 0)
    factory.add_integer_var('x', -512, 512)
    factory.add_integer_var('y', -512, 512)
    
    # e1 := x == y
    e1 = factory.get_top()
    e1 = factory.cond_binary(e1, '>=', 'x', 6)
    e1 = factory.cond_binary(e1, '<=', 'x', 6)
    # e2 := x := x
    e2 = factory.op_binary(e1, 'x', '+', 'x', 0)
    
    assert factory.is_eq(e1, e2) 


def test_dbms_assign_2():
    factory = dbms.DBMFactory(-512, 512)
    factory.add_integer_var(0, 0, 0)
    factory.add_integer_var('x', -512, 512)
    factory.add_integer_var('y', -512, 512)
    # e1 := x = 6
    e1 = factory.get_top()
    e1 = factory.cond_binary(e1, '>=', 'x', 6)
    e1 = factory.cond_binary(e1, '<=', 'x', 6)
    # e2 := x = 8
    e2 = factory.get_top()
    e2 = factory.cond_binary(e2, '>=', 'x', 8)
    e2 = factory.cond_binary(e2, '<=', 'x', 8)
    # e3 := x = 6
    e3 = factory.get_top()
    e3 = factory.cond_binary(e3, '>=', 'x', 6)
    e3 = factory.cond_binary(e3, '<=', 'x', 6)

    assert factory.is_eq(e1, e3)
    # apply x = x + 2
    e1 = factory.op_binary(e1, '+', 'x', 'x', 2)
    assert factory.is_eq(e1, e2) 
    # apply x = x - 1
    e1 = factory.op_binary(e1, '-', 'x', 'x', 1)
    # apply x = x - 1
    e1 = factory.op_binary(e1, '+', 'x', 'x', -1)
    print factory.to_string(e1)
    assert factory.is_eq(e1, e3) 
    
