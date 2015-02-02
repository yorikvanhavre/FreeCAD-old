# -*- coding: utf-8 -*-

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2015 Dan Falck <ddfalck@gmail.com>                      *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************
''' Example Post, using Path.Commands instead of Path.toGCode strings for Path gcode output. '''
import FreeCAD
import Path, PathScripts
from PathScripts import PostUtils

class saveVars(object):
    ''' save settings for moves,feeds,spindle speeds,modal, etc'''
    def __init__(self,value):
        self.val = value
    def retVal(self):
        return self.val

# the following variables help set things up:
moveformat = saveVars(3)    #number of digits behind decimal for xyzijk moves
feedformat = saveVars(1)    #number of digits behind decimal for F feedrate
rpmformat  = saveVars(0)    #number of digits behind decimal for spindle rpm
modalbool  = saveVars(True) #set modal commands ie don't repeat commands and axis moves if they are already in effect
commentsym = saveVars(';')  #comment symbol or symbols change this to the format that your control uses ie '()' or ';'
tlret = '''M5M25
G49H0\n''' #spindle off,height offset canceled,spindle retracted (M25 is centroid command)
toolRet = saveVars(tlret) #line for retracting tool and turning off spindle 
zret = '''G91G28X0Z50
G90\n'''
zeroRet = saveVars(zret) # line for zero return 
safetyblock = saveVars('G90G40G49\n') 
#oldtl = saveVars(0) # load tool 0 
#oldtoolno = saveVars(0)

def fmt(num):
    ''' used for axis moves'''
    dec = moveformat.retVal()
    fnum = '%.*f' % (dec, num)
    return fnum

def ffmt(num):
    ''' used for feedrate'''
    dec = feedformat.retVal()
    fnum = '%.*f' % (dec, num)
    return fnum

def sfmt(num):
    ''' used for spindle rpm'''
    dec = rpmformat.retVal()
    fnum = '%.*f' % (dec, num)
    return fnum

def fcoms(string):
    ''' filter and rebuild comments'''
    com = commentsym.retVal()
    if len(com)==1:
        s1 = string.replace('(', com)
        comment = s1.replace(')', '')
    else:
        return string
    return comment

class saveVals(object):
    ''' save commands info for modal output'''
    def __init__(self, command):
        self.com = command.Name
        self.params = command.Parameters

    def retVals(self):
        return self.com, self.params

def lineout(command, oldvals):
    modal=modalbool.retVal()
    line = ""
    if modal and (oldvals.com == command.Name):
        line +=""
    else:
        if command.Name == 'M6':
            line+= toolRet.retVal()
            line+= zeroRet.retVal()
            line+= 'M6T'+str(int(command.Parameters['T']))
        elif '(' in command.Name: 
            line+= str(fcoms(command.Name))
        else:
            line += str(command.Name)
    if command.Name == 'M3':
        line+= 'S'+str(sfmt(command.Parameters['S']))
    if command.Name == 'M4':
        line+= 'S'+str(sfmt(command.Parameters['S']))
    if 'X' in command.Parameters:
        if oldvals.params and (oldvals.com == command.Name) and modal:
            d =oldvals.params 
            if 'X' in d.keys():
                if d['X']==command.Parameters['X']:
                    pass
                else:
                    line += "X"+str(fmt(command.Parameters['X']))
            else:
                line += "X"+str(fmt(command.Parameters['X']))
        else:
            line += "X"+str(fmt(command.Parameters['X']))

    if 'Y' in command.Parameters:
        if oldvals.params and (oldvals.com == command.Name) and modal:
            d =oldvals.params 
            if 'Y' in d.keys():
                if d['Y']==command.Parameters['Y']:
                    pass
                else:
                    line += "Y"+str(fmt(command.Parameters['Y']))
            else:
                line += "Y"+str(fmt(command.Parameters['Y']))
        else:
            line += "Y"+str(fmt(command.Parameters['Y']))

    if 'Z' in command.Parameters:
        if oldvals.params and (oldvals.com == command.Name) and modal:
            d =oldvals.params 
            if 'Z' in d.keys():
                if d['Z']==command.Parameters['Z']:
                    pass
                else:
                    line += "Z"+str(fmt(command.Parameters['Z']))
            else:
                line += "Z"+str(fmt(command.Parameters['Z']))
        else:
            line += "Z"+str(fmt(command.Parameters['Z']))

    if 'I' in command.Parameters:
        line += "I"+str(fmt(command.Parameters['I']))
    if 'J' in command.Parameters:
        line += "J"+str(fmt(command.Parameters['J']))

    if 'F' in command.Parameters:
        if oldvals.params and modal:
            d =oldvals.params 
            if 'F' in d.keys():
                if d['F']==command.Parameters['F']:
                    pass
                else:
                    line += "F"+str(ffmt(command.Parameters['F']))
            else:
                line += "F"+str(ffmt(command.Parameters['F']))
        else:
            line += "F"+str(ffmt(command.Parameters['F']))
    return line

def firstZ(commands):
    # find first Z move- usefule later for height offsets
    for c in commands:
        if 'Z' in c.Parameters:
            return c


def export(obj,filename):
    commands = obj[0]
    gcode = ''
    oldtoolno = saveVars(0)
    oldtool = False
    if obj[0].Description: #use the Project description for a comment, if there is one
        pcom = '(' +obj[0].Description+ ')'
        projcomment = Path.Command(pcom)
        gcode+= fcoms(projcomment.Name)+'\n'

    # add the so called 'safety block':
    gcode+=safetyblock.retVal()
    # metric or imperial units will be automatically pulled from FreeCAD preferences
    units = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units")
    if units.GetInt('UserSchema') == 0:
        firstcommand = Path.Command('G21') #metric mode
    else:
        firstcommand = Path.Command('G20') #inch mode

    oldvals = saveVals(firstcommand) #save first command for modal use
    fp = obj[0]
    gcode+= firstcommand.Name

    if hasattr(fp,"Path"):
        for c in fp.Path.Commands:
            if c.Name == 'M6':
                if c.Parameters['T']== oldtoolno.retVal():
                    oldtool = True
                else:
                    boguscommand = Path.Command('G999')
                    oldvals = saveVals(boguscommand)
                    gcode+= lineout(c, oldvals)+'\n'
                oldtoolno = saveVars(c.Parameters['T'])
            elif (c.Name == 'M3') or (c.Name == 'M4'):
                if oldtool:
                    pass
                else:
                    gcode+= lineout(c, oldvals)+'\n'
            else:
                gcode+= lineout(c, oldvals)+'\n'
                oldvals = saveVals(c)
        gcode+=toolRet.retVal() #turn off spindle and retract it
        gcode+= zeroRet.retVal() #return to reference 
        gcode+=safetyblock.retVal() #safety block for good measure
        gcode+='M2\n' #end program
        gfile = open(filename,"wb")
        gfile.write(gcode)
        gfile.close()
    else:
        FreeCAD.Console.PrintError('Select a path object and try again\n')
    if obj[0].Editor:
        FreeCAD.Console.PrintMessage('Editor Activated\n')
        dia = PostUtils.GCodeEditorDialog()
        dia.editor.setText(gcode)
        dia.exec_()



