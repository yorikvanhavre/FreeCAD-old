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

def fmt(val): 
    num = eval(val)
    return format(num, '.4f')

def ffmt(val):
    num = eval(val)
    return format(num, '.2f')

def parse(inputstring):
    "parse(inputstring): returns a parsed output string"
    print "postprocessing..."
    
    output = ""
    
    # write some stuff first
    output += "(time:"+str(now)+")\n"
    output += "G17 G21 G80 G40 G90\n"
    output += "(Exported by FreeCAD)\n"
    
    linenr = 100
    lastcommand = None
    # treat the input line by line
    lines = inputstring.split("\n")
    for line in lines:
        wordlist=[]
        # split the G/M command from the arguments
        if " " in line:
            command,args = line.split(" ",1)
            #wordlist.append(command)
            #split up the words in the line
#            if command == 'M3':
#                command.append('\n')
            words = args.split()
            for w in words:
                if w <> ' ':
                    if w[0]<>'K': #remove K
                        wordlist.append(w)
            wordlist.append("\n")
        else:
            # no space found, which means there are no arguments
            command = line
            args = ""
        # add a line number
#        output += "N" + str(linenr) + " "
        # only print the command if it is not the same as the last one
        if command != lastcommand:
            output += command + ""
        for w in wordlist:
            output += w + ""
#        output += args + "\n"
#        t = type(args)
#        output +=args +str(t)+ "\n"
        # increment the line number
#        linenr += 10
        # store the latest command
        lastcommand = command
        
    # write some more stuff at the end
    output += "M05\n"
    output += "G00 X-1.0 Y1.0\n"
    output += "G17 G80 G40 G90\n"
    output += "M2\n"
    
    print "done postprocessing."
    return output

print __name__ + " gcode postprocessor loaded."

