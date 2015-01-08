#***************************************************************************
#*   (c) Yorik van Havre (yorik@uncreated.net) 2014                        *
#*                                                                         *
#*   This file is part of the FreeCAD CAx development system.              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   FreeCAD is distributed in the hope that it will be useful,            *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Lesser General Public License for more details.                   *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with FreeCAD; if not, write to the Free Software        *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************/


'''
This is an example postprocessor file for the Path workbench. It is used to
take a pseudo-gcode fragment outputted by a Path object, and output
real GCode suitable for a particular machine. This postprocessor, once placed 
in the appropriate PathScripts folder, can be used directly from inside FreeCAD,
via the GUI importer or via python scripts with:

import Path
Path.write(object,"/path/to/file.ncc","post_example")

It must contain at least a parse() function, that takes a string as 
argument, which is the pseudo-GCode data from a Path object, and return
another string, which is properly formatted GCode.
'''

import datetime
now = datetime.datetime.now()
from PathScripts import post_editor

OUTPUT_COMMENTS = False
SHOW_EDITOR = True
USE_LINE_NUMBERS = True
MODAL = False #if true commands are suppressed if the same as previous line.
COMMAND_SPACE = ""

LINENR = 100 #line number starting value

#Preamble text will appear at the beginning of the GCODE output file.
PREAMBLE = '''G17 G21 G80 G40 G90
'''
#Postamble text will appear following the last operation.
POSTAMBLE = '''M05
G00 X-1.0 Y1.0
G17 G80 G40 G90
M2
'''
 
#Pre operation text will be inserted before every operation
PRE_OPERATION = '''
 
'''
 
#Post operation text will be inserted after every operation
POST_OPERATION = '''

'''

def fmt(val): 
    num = eval(val)
    return format(num, '.4f')

def ffmt(val):
    num = eval(val)
    return format(num, '.2f')

def linenumber():
    global LINENR
    if USE_LINE_NUMBERS == True:
        LINENR += 10 
        return "N" + str(LINENR) + " "
    return ""

def parse(inputstring):
    "parse(inputstring): returns a parsed output string"
    print "postprocessing..."
    
    output = ""
    
    # write some stuff first
    if OUTPUT_COMMENTS:
        output += linenumber() + "(Exported by FreeCAD)\n"
        output += linenumber() + "(Post Processor: " + __name__ +")\n"
        output += linenumber() + "(Output Time:"+str(now)+")\n"
    #Write the preamble 
    if OUTPUT_COMMENTS: output += linenumber() + "(begin preamble)\n"
    for line in PREAMBLE.splitlines(True):
        output += linenumber() + line

    lastcommand = None
    
    # treat the input line by line
    lines = inputstring.splitlines(True)
    for line in lines:
        wordlist = [a.strip() for a in line.split(" ")]
        
        # if modal only print the command if it is not the same as the last one
        command = wordlist[0]
        if MODAL == False:
            if command == lastcommand:
                wordlist.pop(0) 

        #remove the 'k' words.  Ask Dan about this
        indices = [i for i, s in enumerate(wordlist) if 'K' in s]
        if len(indices) <> 0:
            wordlist.pop(indices[0])

        # store the latest command
        lastcommand = command

        #Insert a line number and newline 
        if USE_LINE_NUMBERS: wordlist.insert(0,(linenumber()))
        wordlist.append("\n")

        #dump to output
        for w in wordlist:
            output += w + COMMAND_SPACE

    # write some more stuff at the end
    if OUTPUT_COMMENTS: output += "(begin postamble)\n" 
    for line in POSTAMBLE.splitlines(True):
        output += linenumber() + line

    print "done postprocessing."
    return output



print __name__ + " gcode postprocessor loaded."
