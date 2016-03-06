import pytest

import graph_algorithms
import dbms

def test_dbm_set_weight_get_weight():

    d = dbms.DBM()
    d.set_weight(1, 3, 2)
    assert d.get_weight(1, 2) == 3
    d.set_weight(2, 4, 2)
    d.set_weight(1, -99, 2)
    assert d.get_weight(1, 2) == -99
    assert d.get_weight(2, 2) == 4
    d.set_weight(2, None, 2)
    assert d.get_weight(2, 2) is None
    d.set_weight(1, None, 2)
    assert d.get_weight(1, 2) is None
    assert d.get_weight("", 3) is None
    d.set_weight(1, 10, 2)
    d.set_weight(2, -10, 2)
    d.set_weight(1, 1, 3)
    d.set_weight(3, 0, 3)
    assert d.get_weight(3, 3) == 0
    assert d.get_weight(1, 1) is None
    assert d.get_weight(2, 2) == -10
    
def test_dbm_copy():
    
    d = dbms.DBM()
    x = [1,2]
    y = [3,4]
    d.set_weight(1, x , 2)
    d.set_weight(2, y, 2)
    d2 = d.copy()
    assert d.to_string() == d2.to_string() # == d2.to_string()

def test_dbm_exists_negative_cycle():

    d1 = dbms.DBM()
    d1.set_weight(1, 1, 2)
    d1.set_weight(2, -2, 1)
    assert d1.exists_negative_cycle()
    d2 = dbms.DBM()
    d2.set_weight(1, -2, 2)
    d2.set_weight(2, 3, 1)
    assert not d2.exists_negative_cycle()
    d3 = dbms.DBM()
    for i in range(0, 500):
        d3.set_weight(i, i*((-1)**(i % 2)), i+1)
    d3.set_weight(500, 100, 50)
    assert d3.exists_negative_cycle()
    d3.set_weight(500, 100000000, 50)
    assert not d3.exists_negative_cycle()
    
def test_dbm_find_shortest_paths():

    # example from wikipedia, slightly extended
    d1 = dbms.DBM()
    d1.set_weight(1, -2, 3)
    d1.set_weight(3, 2, 4)
    d1.set_weight(4, -1, 2)
    d1.set_weight(2, 4, 1)
    d1.set_weight(2, 3, 3)
    d1.set_weight(5, 10, 5)
    d2 = d1.find_shortest_paths()
    assert d2.get_weight(1, 1) == 0
    assert d2.get_weight(1, 2) == -1
    assert d2.get_weight(1, 3) == -2
    assert d2.get_weight(1, 4) == 0
    assert d2.get_weight(2, 1) == 4
    assert d2.get_weight(2, 2) == 0
    assert d2.get_weight(2, 3) == 2
    assert d2.get_weight(2, 4) == 4
    assert d2.get_weight(3, 1) == 5
    assert d2.get_weight(3, 2) == 1
    assert d2.get_weight(3, 3) == 0
    assert d2.get_weight(3, 4) == 2
    assert d2.get_weight(4, 1) == 3
    assert d2.get_weight(4, 2) == -1
    assert d2.get_weight(4, 3) == 1
    assert d2.get_weight(4, 4) == 0
    assert d2.get_weight(5, 1) is None
    assert d2.get_weight(5, 2) is None
    assert d2.get_weight(5, 3) is None
    assert d2.get_weight(5, 4) is None
    assert d2.get_weight(5, 5) == 0
    assert d2.get_weight(1, 5) is None
    assert d2.get_weight(2, 5) is None
    assert d2.get_weight(3, 5) is None
    assert d2.get_weight(4, 5) is None

    
