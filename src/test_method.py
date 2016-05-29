
from code_rep.module import *
from code_rep.method import *
from analysis.eval import *
from code_rep.variable import Variable
from code_rep.type_system import Integer
from code_rep.instr import DirectAssignment
from code_rep.variable import Variable

from domains import boxes

import analyzers

def test_4():
    #
    # int summe(int x, int y)
    # {
    #   return x+y;
    # }
    # int main()
    # {
    #   int x = 11;
    #   int y = 42;
    #   return summe(x, y);
    # }
    mod1 = Module('module')

    # summe
    vx = Variable('x', Integer(-1024, 1024))
    vy = Variable('y', Integer(-1024, 1024))
    vr = Variable('ret', Integer(-1024, 1024))
    a3 = DirectAssignment(vr, ['+', vx, vy])
    # (1) create initial and final basic blocks
    summe = Method('summe', mod1)
    summe_1 = summe.initial
    summe_2 = summe.final
    summe_2.append_instruction(a3)
    # (2) add parameters and local variables (including return variable)
    summe.add_parameter(vx)
    summe.add_parameter(vy)
    summe.add_local_variable(vr)
    summe.set_return_variable(vr)
    # (3) add edges
    summe.set_edge(summe_1, summe_2, None, None)

    # main
    # (1) create initial and final basic blocks
    vx = Variable('a', Integer(-1024, 1024))
    vy = Variable('b', Integer(-1024, 1024))
    vr = Variable('ret', Integer(-1024, 1024))
    main = Method('main', mod1)
    main.add_local_variable(vx)
    main.add_local_variable(vy)
    main.add_local_variable(vr)
    main.set_return_variable(vr)
    
    main_1 = main.initial
    main_2 = main.final
    
    a1 = DirectAssignment(vx, [3])
    a2 = DirectAssignment(vy, [2])
    main_1.append_instruction(a1)
    main_1.append_instruction(a2)
    i1 = mod1.create_invocation(main, summe, [vx, vy], vr)
    main.set_edge(main_1, main_2, None, i1)
    
    mod1.initial = main
    mod1.final = main
    dom = boxes.BoxDomainFactory(-1024, 1024)
    m_analyzer = analyzers.Module0CFAForwardAnalyzer(mod1, dom)
    print m_analyzer._forward_sequence
    m_analyzer.analyze(dom.get_top(), dom.get_bot(), 5)

test_4()
