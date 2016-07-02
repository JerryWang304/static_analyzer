
from code_rep.module import *
from code_rep.method import *
from analysis.eval import *

# example:
#
# int foo(int x, int y)
# {
#    return x+y;
# }
#
# int bar(int x)
# {
#    foo(x, x); return bar(x);
# }
#
# int main()
# {
#   bar();
# }
#

foo_1 = BasicBlock(1, [])
foo_2 = BasicBlock(2, [])
bar_1 = BasicBlock(1, [])
bar_2 = BasicBlock(2, [])
bar_3 = BasicBlock(3, [])
main_1 = BasicBlock(1, [])
main_2 = BasicBlock(2, [])

mod1 = Module('module')

foo = Method('foo', mod1, foo_1, foo_2, [], None)
foo.set_edge(foo_1, foo_2, None, None)
bar = Method('bar', mod1, bar_1, bar_3, [], None)
bar.add_blocks(bar_2)
bar.set_edge(bar_1, bar_2, None, Invocation(foo, [], None))
bar.set_edge(bar_2, bar_3, None, Invocation(bar, [], None))
main = Method('main', mod1, main_1, main_2, [], None)
main.set_edge(main_1, main_2, None, Invocation(bar, [], None))

mod1.create_call_graph()
print mod1.callgraph_to_string()



prog = Module('main')

b1 = BasicBlock(1, [instr.ConstantAssignment('x', 0),
                    instr.Alloc('y', 'int', 100)])
b2 = BasicBlock(2, [instr.Load('z', 'x')])
b3 = BasicBlock(3, [instr.Store('p', 'x')])
b4 = BasicBlock(4, [instr.Address('q', 'y')])
b5 = BasicBlock(5, [])


#        /--> b3--\
# b1 -> b2         --> b5
#        \--> b4--/

m = Method('foo', prog, b1, b5, [], None)
m.add_blocks(b2, b3, b4)
m.set_edge(b1, b2)
m.set_edge(b2, b3, None, Invocation(m, ['x', 'y'], None))
m.set_edge(b2, b4)
m.set_edge(b3, b5)
m.set_edge(b4, b5)
print m


