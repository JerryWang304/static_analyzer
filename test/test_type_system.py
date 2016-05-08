import pytest
from type_system import *

def test_integer_types():
    i1 = Integer(0, 127)
    i2 = Integer(0, 127)
    i3 = Integer(0, 129)
    i4 = Integer(-100, 100)
    assert (i1 == i2)
    assert (i1 != i3)
    assert (i1 != i4)
    assert (i2 != i3)
    assert (i2 != i4)
    assert (i3 != i4)
    d = {}
    d[i1] = True
    assert (i2 in d)
    assert (i3 not in d)
    assert (i4 not in d)
    
def test_pointer_types():
    i1 = Integer(-30, 127)
    i2 = Integer(-30, 127)
    i3 = Integer(-1000, 1299)
    p1 = Pointer(i1)
    p2 = Pointer(i2)
    p3 = Pointer(i3)
    p4 = Pointer(Pointer(i1))
    p5 = Pointer(Pointer(i1))
    assert (p1 == p2)
    assert (p2 != p3)
    assert (p4 == p5)
    d = {}
    d[p1] = True
    d[p4] = True
    assert (p2 in d)
    assert (p5 in d)
    assert (p3 not in d)
