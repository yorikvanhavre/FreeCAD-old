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
from PathScripts import PostUtils

OUTPUT_COMMENTS = True
OUTPUT_HEADER = True
OUTPUT_LINE_NUMBERS = False
SHOW_EDITOR = True
MODAL = False #if true commands are suppressed if the same as previous line.
COMMAND_SPACE = ""
LINENR = 100 #line number starting value


#Preamble text will appear at the beginning of the GCODE output file.
PREAMBLE = '''G17 G21 G90
'''
#Postamble text will appear following the last operation.
POSTAMBLE = '''M05
G00 X-1.0 Y1.0
G17 G90
M2
'''
 
#Pre operation text will be inserted before every operation
PRE_OPERATION = '''
 
'''
 
#Post operation text will be inserted after every operation
POST_OPERATION = '''

'''

#Tool Change commands will be inserted before a tool change
TOOL_CHANGE = '''(A tool change)
(happens here)
'''

def linenumber():
    global LINENR
    if OUTPUT_LINE_NUMBERS == True:
        LINENR += 10 
        return "N" + str(LINENR) + " "
    return ""

def parse(inputstring):
    "parse(inputstring): returns a parsed output string"
    print "postprocessing..."
    
    output = ""
    lastcommand = None

    #params = ['X','Y','Z','A','B','I','J','K','F','S'] #This list control the order of parameters
    params = ['X','Y','Z','A','B','I','J','F','S','T'] #linuxcnc doesn't want K properties on XY plane  Arcs need work.
    
    # write header
    if OUTPUT_HEADER:
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
        commandline = PostUtils.stringsplit(line)
        outstring = []
        command = commandline['command']
        outstring.append(command) 
        # if modal: only print the command if it is not the same as the last one
        if MODAL == True:
            if command == lastcommand:
                outstring.pop(0) 

        # Now add the remaining parameters in order
        for param in params:
            if commandline[param]: 
                if param == 'F': 
                    outstring.append(param + format(eval(commandline[param]), '.2f'))
                elif param == 'T':
                    outstring.append(param + (commandline[param]))
                else:
                    outstring.append(param + format(eval(commandline[param]), '.4f'))
        

        # store the latest command
        lastcommand = command

        # Check for Tool Change: 
        if command == 'M6':
            if OUTPUT_COMMENTS: output += "(begin toolchange)\n" 
            for line in TOOL_CHANGE.splitlines(True):
                output += linenumber() + line

        if command == "message":
          if OUTPUT_COMMENTS == False:
            outstring = []
          else:
            outstring.pop(0) #remove the command

        #prepend a line number and append a newline
        if len(outstring) >= 1:
            if OUTPUT_LINE_NUMBERS: 
                outstring.insert(0,(linenumber()))
            outstring.append("\n")

            #append the line to the final output
            for w in outstring:
                output += w + COMMAND_SPACE
    
    # write some stuff at the end
    if OUTPUT_COMMENTS: output += "(begin postamble)\n" 
    for line in POSTAMBLE.splitlines(True):
        output += linenumber() + line

    if SHOW_EDITOR:
        dia = PostUtils.GCodeEditorDialog()
        dia.editor.setText(output)
        result = dia.exec_()
        if result:
            final = dia.editor.toPlainText()
        else:
            final = output
    else:
        final = output
      
    print "done postprocessing."
    return final
   
    
print __name__ + " gcode postprocessor loaded."

