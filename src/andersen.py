##############################
#
# andersen.py 
#
# Primitive implementation of
# Andersen pointer analysis.
#
#
# (C) 2016, Andreas Gaiser
##############################

from code_rep.instr import *
from code_rep.type_system import Integer, Pointer
import os
import z3

class AndersenAnalysis(object):
    
    #
    # Locations:
    # - allocations ("new ...")
    # - parameters
    # - local variables
    #

    #
    # PointsTo map:
    # Locations --> Locations
    #
    #


    def __init__(self, module):
        self._module = module

    def create_z3_fp_program(self):
        fp = z3.Fixedpoint()
        fp.set(engine='datalog')
        
        loc_sort = z3.BitVecSort(32)

        result = ''
        locations = {}
        inv_locations = {}
        counter = 0
        for method in self._module.methods():
            for param in  method.parameters():
                locations[param] = counter
                inv_locations[counter] = param
                counter += 1
            for local_var in method.local_variables():
                locations[local_var] = counter
                inv_locations[counter] = local_var
                counter += 1
            for alloc in method.allocations():
                locations[alloc] = counter
                inv_locations[counter] = alloc
                counter += 1

        points_to = z3.Function('points_to', loc_sort, loc_sort, z3.BoolSort())
        X, Y, Z = z3.BitVecs('X Y Z', loc_sort)
        fp.declare_var(X, Y, Z)
        fp.register_relation(points_to)
        for method in self._module.methods():
            print Store
            for block in method.blocks():
                for instruction in block.instructions():
                    if isinstance(instruction, Address):
                        # X := &Y
                        # X -> Y
                        c1 = z3.BitVecVal(locations[instruction.target], loc_sort)
                        c2 = z3.BitVecVal(locations[instruction.rhs], loc_sort)
                        fp.fact(points_to(c1, c2))
                    elif isinstance(instruction, DirectVariableAssignment):
                        # X := Y
                        # All Z: Y -> Z => X -> Z
                        if isinstance(instruction.target.get_type(), Pointer):
                            c1 = z3.BitVecVal(locations[instruction.target], loc_sort)
                            c2 = z3.BitVecVal(locations[instruction.source], loc_sort)
                            fp.rule(points_to(c1, X), [points_to(c2, X)])
                    elif isinstance(instruction, Load):
                        
                        # X := *Y
                        # ALL Z1, Z2: Y -> Z1 && Z1 -> Z2 => X -> Z2
                        c1 = z3.BitVecVal(locations[instruction.target], loc_sort)
                        c2 = z3.BitVecVal(locations[instruction.rhs], loc_sort)
                        fp.rule(points_to(c1, Y),
                                [points_to(c2, X), points_to(X, Y)])

                    elif isinstance(instruction, Store):
                        # *X := Y
                        # ALL Z1, Z2: X -> Z1 && Y -> Z2 => Z1 -> Z2

                        if isinstance(instruction.rhs.get_type(), Pointer):
                            c1 = z3.BitVecVal(locations[instruction.target], loc_sort)
                            c2 = z3.BitVecVal(locations[instruction.rhs], loc_sort)
                            fp.rule(points_to(X, Y),
                                    [points_to(c1, X), points_to(c2, Y)])
                
        print 'FP: %s' % fp                    
        fp.query(points_to(X, Y))
        
        print 'Q: %s' % fp.get_answer()
        answer = fp.get_answer()
        print answer.arg(0).children()[0]
        print answer.arg(0).children()[1]
        print inv_locations
        for i in xrange(0, answer.num_args()):
            p1 = (answer.arg(i).children()[0].arg(1)).as_long()
            p2 = (answer.arg(i).children()[1].arg(1)).as_long()
            print '%s points to %s.' % (inv_locations[p1],
                                        inv_locations[p2])
        
        
    def _create_datalog_file(self):
        #
        # One relation PointsTo subseteq Locations X Locations
        #
        # Collect all locations
        #
        result = ''
        locations = {}
        inv_locations = {}
        counter = 0
        for method in self._module.methods():
            for param in  method.parameters():
                locations[counter] = param
                inv_locations[param] = counter
                counter += 1
            for local_var in method.local_variables():
                locations[counter] = local_var
                inv_locations[local_var] = counter
                counter += 1
            for alloc in method.allocations():
                locations[counter] = alloc
                inv_locations[alloc] = counter
                counter += 1

        result += 'LOC %s\n' % len(locations)
        result += 'PointsTo(x: LOC, y: LOC) printtuples\n'

        for method in self._module.methods():

            for block in method.blocks():
                for instruction in block.instructions():
                    if isinstance(instruction, Address):
                        # X := &Y
                        # X -> Y 
                        result += ('PointsTo("LOC%s", "LOC%s").\n' %
                                   (inv_locations[instruction.target],
                                    inv_locations[instruction.rhs]))
                    elif isinstance(instruction, DirectVariableAssignment):
                        # X := Y
                        # All Z: Y -> Z => X -> Z
                        if isinstance(instruction.target.get_type(), Pointer):
                            result += ('PointsTo("LOC%s", x) :- PointsTo("LOC%s", x).\n'
                                       % (inv_locations[instruction.target],
                                          inv_locations[instruction.source]))
                    elif isinstance(instruction, Load):
                        # X := *Y
                        # ALL Z1, Z2: Y -> Z1 && Z1 -> Z2 => X -> Z2
                        result += ('PointsTo("LOC%s", Z2) :- '
                                   'PointsTo("LOC%s", Z1), PointsTo(Z1, Z2).\n'
                                   % (inv_locations[instruction.target],
                                      inv_locations[instruction.rhs]))
                    elif isinstance(instruction, Store):
                        # *X := Y
                        # ALL Z1, Z2: X -> Z1 && Y -> Z2 => Z1 -> Z2

                        if isinstance(instruction.rhs.get_type(), Pointer):
                            result += ('PointsTo(z1, z2) :- '
                                       'PointsTo("LOC%s", z1), PointsTo("LOC%s", z2).\n'
                                       % (inv_locations[instruction.target],
                                          inv_locations[instruction.rhs]))          

                            
        def datalog_solve(program, filename, numberingtype="scc"):
            java_cmd = '..\\bddbddb-full.jar'
            print program
            f = file (filename, "wt")
            print>>f, program
            f.close()
            cmd = 'java -cp %s -mx600m -Dlearnbestorder=n -Dsingleignore=yes -Dbasedir=./results/ -Dbddcache=1500000 -Dbddnodes=40000000 -Dpa.clinit=no -Dpa.filternull=yes -Dpa.unknowntypes=no net.sf.bddbddb.Solver %s' % (java_cmd, filename)
            w = ' net.sf.bddbddb.Solver'
            print cmd
            (in_p, out_p) = os.popen2(cmd)
            result_str = out_p.read()
            out_p.close()    
            in_p.close()
            #print result_str
            result = ''
            for line in result_str.splitlines():
                line = line.strip()
                print "**", line
                if line.startswith('(x=LOC'):
                    result += '%s\n' % line
            return result

        print datalog_solve(result, 'testle')
        for el in inv_locations:
            print "%s => %s" % (el, inv_locations[el])
