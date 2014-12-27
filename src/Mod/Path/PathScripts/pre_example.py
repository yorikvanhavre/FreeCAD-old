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
This is an example preprocessor file for the Path workbench. Its aim is to
parse the contents of a given GCode file, and transform it to make it
suitable for use in a Path object. This preprocessor, once placed in the
appropriate PathScripts folder, can be used directly from inside FreeCAD,
via the GUI importer or via python scripts with:

import Path
Path.read("/path/to/file.ncc","DocumentName","pre_example")

It must contain at least a parse() function, that takes a string as 
argument, which is the unmodified contents of the input GCode file, and 
returns another string, that must respect the following 
rules in order to be used by the Path workbench:

- All lines must begin with a G or M command. Lines that don't respect that 
  rule will be discarded on import.
- Only one occurence of another letter can happen after a G  or M command. 
  For example this is invalid:
    G1 X1 Y2 
    X2 Y3
  You must write it like this: 
    G1 X1 Y2 
    G1 X2 Y3
- Center coordinates (I,J) in G2 and G3 arcs are relative to the last point.
'''

def parse(inputstring):
    "parse(inputstring): returns a parsed output string"
    print "preprocessing..."
    
    # split the input by line
    lines = inputstring.split("\n")
    output = ""
    lastcommand = None
    
    for l in lines:
        # remove any leftover trailing and preceding spaces
        l = l.strip()
        if not l:
            # discard empty lines
            continue
        if l[0].upper() in ["N"]:
            # remove line numbers
            l = l.split(" ",1)[1]
        if l[0] in ["(","%","#"]:
            # discard comment and other non strictly gcode lines
            continue
        if l[0].upper() in ["G","M"]:
            # found a G or M command: we store it
            output += l + "\n"
            last = l[0].upper()
            for c in l[1:]:
                if not c.isdigit():
                    break
                else:
                    last += c
            lastcommand = last
        elif lastcommand:
            # no G or M command: we repeat the last one
            output += lastcommand + " " + l + "\n"
            
    print "done preprocessing."
    return output

print __name__ + " gcode preprocessor loaded."

