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

    def _compute_datalog_file(self):
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

        for l in locations:
            print ('>%s' % l)

        result += 'LOC %s\n' % len(locations)
        result += 'PointsTo(x: LOC, y: LOC) printtuples\n'

        for method in self._module.methods():
            for block in method.blocks():
                for instruction in block.instructions():
                    if isinstance(instruction, Address):
                        result += ('PointsTo("LOC%s", "LOC%s").\n' %
                                   (inv_locations[instruction.target],
                                    inv_locations[instruction.rhs]))
                    elif isinstance(instruction, DirectAssignment):
                        if isinstance(instruction.target, Pointer):
                            result += ('PointsTo("LOC%s", x) :- PointsTo("LOC%s", x).\n'  % (inv_locations[instruction.target],
                                                                                             inv_locations[instruction.rhs]))
                    
                            
        print result
