import sys

import boxes
import dbms
import decision_diagrams
from simple_analyzer import *
from bauhaus import ir 

def int_range(variable_node):
    type_node = variable_node.Its_Type
    return (type_node.Min, type_node.Max)

def compute_cfg(lir_method):

    def get_var(node):
        if 'Name' in node and node.Name != '':
            return ('%s(%s)' % (node.Name, node.number()))
        else:
            return ('unnamed(%s)' % (node.number()))

    def get_block(node):
        return '%s(%s)' % (node.type(), node.number())
    
    cfg = MethodCFG(get_block(lir_method.Basic_Blocks[0]),
                     get_block(lir_method.Basic_Blocks[-1]))

    # add local variables
    inner_factory =  dbms.DBMFactory(-128, 128)
    factory = decision_diagrams.DecisionDiagramFactory(inner_factory)
    
    #factory = boxes.BoxDomainFactory(-128, 128)

    ##factory = dbms.DBMFactory(-128, 128)
    #decision_diagrams.DecisionDiagramFactory(inner_factory)
    
    
    bool_vars = set()
    all_vars = set()
    
    for variable in lir_method.Variables:
        (l, r) = int_range(variable)
        all_vars.add(variable)
        # factory.add_integer_var(get_var(variable), l, r)

    for block in lir_method.Basic_Blocks[1:-1]:
        cfg.add_control_loc(get_block(block), block.is_of_type('CFG_If_Block'))
        #block.is_of_type('CFG_Loop_Header_Jump_Block'))
        #                    (or
        #                     block.is_of_type('CFG_Jump_Back_Block') or
        #                     block.is_of_type('CFG_If_Block')))

    for block in lir_method.Basic_Blocks:
        # add helpers
        if block.is_of_type('CFG_Standard_Block'):
            for helper in block.Helpers:
                all_vars.add(helper)
        if 'Code' in block:
            for instr in block.Code:
                if instr.is_of_type('Integer_Literal_Instruction'):
                    factory.add_constant(instr.Value)
                elif instr.is_of_type('Relational_Instruction'):
                    bool_vars.add(instr.Left.The_Object)
        if block.is_of_type('CFG_If_Block'):
            bool_vars.add(block.Code[-1].Left.The_Object)


    if lir_method.Return_Value.__nonzero__:
        all_vars.add(lir_method.Return_Value)

    all_vars = all_vars | bool_vars
    for variable in all_vars:
        if variable in bool_vars:
            factory.add_bool_var(get_var(variable))
        else:
            (l, r) = int_range(variable)
            factory.add_integer_var(get_var(variable), l, r)
            
        
    def create_simple_connection(source_loc, code, target_loc):
        assignments = []
        # TODO: right now, assume Conditional expression comes at the end!
        
        for instr in code:
            if instr.is_of_type('Integer_Literal_Instruction'):
                value = instr.Value
                target = instr.Left.The_Object
                assignments.append([get_var(target), [value]])
            elif instr.is_of_type('Arithmetic_Add_Instruction'):
                first = instr.First.The_Object
                second = instr.Second.The_Object
                target = instr.Left.The_Object
                assignments.append([get_var(target),
                                    ['+', get_var(first), get_var(second)]])
            elif instr.is_of_type('Modulo_Instruction'):
                first = instr.First.The_Object
                second = instr.Second.The_Object
                target = instr.Left.The_Object
                assignments.append([get_var(target),
                                    ['%', get_var(first), get_var(second)]])
            elif instr.is_of_type('Arithmetic_Subtract_Instruction'):
                first = instr.First.The_Object
                second = instr.Second.The_Object
                target = instr.Left.The_Object
                assignments.append([get_var(target),
                                    ['-', get_var(first), get_var(second)]])
            elif instr.is_of_type('Copy_Assignment_Instruction'):
                source = instr.Right.The_Object
                target = instr.Left.The_Object
                assignments.append([get_var(target), [get_var(source)]])
            elif instr.is_of_type('Relational_Instruction'):
                op = ''
                if instr.is_of_type('Greater_Than_Instruction'):
                    op = '>'
                elif instr.is_of_type('Greater_Or_Equal_Instruction'):
                    op = '>='
                elif instr.is_of_type('Less_Than_Instruction'):
                    op = '<'
                elif instr.is_of_type('Less_Or_Equal_Instruction'):
                    op = '<='
                elif instr.is_of_type('Unequal_Instruction'):
                    op = '!='
                elif instr.is_of_type('Equal_Instruction'):
                    op = '=='
                else:
                    print 'Unknown conditional operation.'
                    op = ''
                first = instr.First.The_Object
                second = instr.Second.The_Object
                target = instr.Left.The_Object
                assignments.append([get_var(target),
                                    [op, get_var(first), get_var(second)]])
                
            else:
                print('Unknown instruction: %s' % instr.type())
        cfg.set_edge(source_loc, target_loc, None, assignments)
                

    def create_if_connection(source, if_target, else_target, code):
        if_intermediate = (source, 'i')
        cfg.add_control_loc(if_intermediate)
        last = code[-1]
        create_simple_connection(source, code, if_intermediate)
        target = last.Left.The_Object # last instr should always be def-like
        cfg.set_edge(if_intermediate,
                     if_target,
                     ['!=', get_var(target), 0], [])
        cfg.set_edge(if_intermediate,
                     else_target,
                     ['==', get_var(target), 0], [])
            
    for block in lir_method.Basic_Blocks:

        # CFG blocks
        if block.is_of_type('CFG_Entry_Block'):
            cfg.set_edge(get_block(block), get_block(block.Next), None, [])
        elif block.is_of_type('CFG_Single_Successor_Block'):
            create_simple_connection(get_block(block), block.Code, get_block(block.Next))
        elif block.is_of_type('CFG_If_Block'):
            create_if_connection(get_block(block),
                                 get_block(block.Then_Next),
                                 get_block(block.Else_Next),
                                 block.Code)
        elif block.is_of_type('CFG_Return_Value_Block'):
            pass
        
    return (cfg, factory)


if __name__ == '__main__':
    graph = ir.Graph(sys.argv[1])
    for function in graph.nodes_of_type(ir.Logical, 'Nothrow_Function'):
        if function.Name == sys.argv[2]:
            (cfg, dom) = compute_cfg(function)
            print cfg.to_string()
            cfg.forward_analyze(dom, dom.get_top(), dom.get_bot(), 55)
