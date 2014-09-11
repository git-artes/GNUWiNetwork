#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    This file is part of GNUWiNetwork,
#    Copyright (C) 2014 by 
#        Pablo Belzarena, Gabriel Gomez Sena, Victor Gonzalez Barbone,
#        Facultad de Ingenieria, Universidad de la Republica, Uruguay.
#
#    GNUWiNetwork is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GNUWiNetwork is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GNUWiNetwork.  If not, see <http://www.gnu.org/licenses/>.
#


'''Example code for the Epydoc documentation generation.

This module shows the use of the Epytext markup language for the automatic generation of Python Documentation. The first line is a brief description of the module; it should fit in a line, end in '.' and be followed by a blank line. Text describing the module follows. Please see I{The Epytext markup language} page, reference below, for a more complete description of the Epytext markup language.

Start all modules with these lines, to indicate the where is the Python interpreter and the character coding of the module::

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
'''

# place imports here, one import per line

# place module constants and variables here

'''
@var mod_var1: a module variable.
'''
mod_var1 = 'epydoc_example module'



class ClassA:
    '''A brief description of class ClassA, should fit in a line.
  
    A detailed description of class ClassA, may expand on several lines.
    @cvar cl_attr1: a class attribute, common to all instancess. This variable counts how many times this class has been instantiated.
    @ivar in_attr1: an instance attribute.
    '''
    cl_attr1 = 0  # a class attribute, no 'self' before

  
    def __init__(self):
        '''A brief description of the constructor, if necessary.
    
        A detailed description of the constructor, if necessary.
        '''
        self.in_attr1 =  None   # an instance attribute, 'self' before

        ClaseA.cl_attr1 += 1    # increments on each instantiation
        pass

    
    def __str__(self):
        '''Representation of this class on C{print}.
        '''
        ss = 'ClassA instance, cl_attr1={0}, in_attr1={1}'.format( \
            self.cl_attr1, self.in_attr1)
        return ss

    
    def __eq__(self, ob):
        '''Overwriting of the equals operator, defines equality between instances.
    
        Two instances will considered "equal" if attribute in_attr has the same value in both instances.
        '''
        if self.in_attr1 == ob.in_attr1:
            return True
        else:
            return False

      
    def afunc1(self, par1, par2='the two'):
        '''Brief description of function.
    
        Detailed description of function.
        @param par1: first positional parameter, no default value given.
        @param par2: second positional parameter, with default falue. May be also considered a keyword parameter.
        @return: the return value.
        '''
    pass
    

