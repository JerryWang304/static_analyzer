
from code_rep.module import *
from code_rep.method import *
from analysis.eval import *
from code_rep.variable import Variable
from code_rep.type_system import Integer
from code_rep.instr import DirectAssignment
from code_rep.variable import Variable

from domains import boxes
from domains import dbms
from domains import decision_diagrams

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


def test_5():
    #
    # int summe(int x, int y)
    # {
    #   return x+y;
    # }
    # int main()
    # {
    #   int c = UNDEF;
    #   int x = 11;
    #   int y = 42;
    #   if (c)
    #     return summe(x, y);
    #   else
    #     return 100;
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
    
    vc = Variable('c', Integer(0, 1))
    vx = Variable('a', Integer(-1024, 1024))
    vy = Variable('b', Integer(-1024, 1024))
    vr = Variable('ret', Integer(-1024, 1024))
    main = Method('main', mod1)
    main.add_local_variable(vc)
    main.add_local_variable(vx)
    main.add_local_variable(vy)
    main.add_local_variable(vr)
    main.set_return_variable(vr)
    main_1 = main.initial
    main_2 = main.final
    main_b1 = BasicBlock(3)
    main_b2 = BasicBlock(3)
    main.add_block(main_b1)
    main.add_block(main_b2)
    a1 = DirectAssignment(vx, [3])
    a2 = DirectAssignment(vy, [2])
    main_1.append_instruction(a1)
    main_1.append_instruction(a2)
    a3 = DirectAssignment(vr, [100])
    i1 = mod1.create_invocation(main, summe, [vx, vy], vr)
    main_b2.append_instruction(a3)
    main.set_edge(main_1, main_b1, ['==', vc, 1], None)
    main.set_edge(main_1, main_b2, ['==', vc, 0], None)
    main.set_edge(main_b1, main_2, None, i1)
    main.set_edge(main_b2, main_2, None, None)
    mod1.initial = main
    mod1.final = main
    inner_dom = boxes.BoxDomainFactory(-1024, 1024)
    dom = decision_diagrams.DecisionDiagramFactory(inner_dom)
    m_analyzer = analyzers.Module0CFAForwardAnalyzer(mod1, dom)
    print m_analyzer._forward_sequence
    m_analyzer.analyze(dom.get_top(), dom.get_bot(), 5)

def test_6():
    mod1 = Module('module')
    
    # summe
    vx = Variable('x', Integer(-1024, 1024))
    vy = Variable('y', Integer(-1024, 1024))
    vr = Variable('ret', Integer(-1024, 1024))
    a1 = DirectAssignment(vx, [0])
    a2 = DirectAssignment(vy, [0])
    a3 = DirectAssignment(vx, ['+', vx, 1])
    a4 = DirectAssignment(vy, ['+', vy, 1])
    a5 = DirectAssignment(vx, ['+', vx, 1])
    a6 = DirectAssignment(vy, ['-', vy, 1])
    
    main = Method('main', mod1)
    main.add_local_variable(vx)
    main.add_local_variable(vy)
    main.add_local_variable(vr)
    main.set_return_variable(vr)

    main_init = main.initial
    main_final = main.final
    main_while = BasicBlock('while')
    main_if = BasicBlock('if')
    main_b1 = BasicBlock('b1')
    main_b2 = BasicBlock('b2')

    main.add_block(main_while)
    main.add_block(main_if)
    main.add_block(main_b1)
    main.add_block(main_b2)
    
    main.set_edge(main_init, main_while, None, None)
    main.set_edge(main_while, main_if, ['<=', vx, 999], None)
    main.set_edge(main_while, main_final, ['>=', vx, 1000], None)
    main.set_edge(main_if, main_b1, ['<=', vx, 499], None)
    main.set_edge(main_if, main_b2, ['>', vx, 499], None)
    main.set_edge(main_b1, main_while, None , None)
    main.set_edge(main_b2, main_while, None, None)  

    main_init.append_instruction(a1)
    main_init.append_instruction(a2)
    main_b1.append_instruction(a3)
    main_b1.append_instruction(a4)
    main_b2.append_instruction(a5)
    main_b2.append_instruction(a6)
    
    
    mod1.initial = main
    mod1.final = main
    inner_dom = boxes.BoxDomainFactory(-1024, 1024)
    dom = decision_diagrams.DecisionDiagramFactory(inner_dom)
    m_analyzer = analyzers.Module0CFAForwardAnalyzer(mod1, dom)
    print m_analyzer._forward_sequence
    m_analyzer.analyze(dom.get_top(), dom.get_bot(), 5)

    
#test_4()
test_5()
test_6()
