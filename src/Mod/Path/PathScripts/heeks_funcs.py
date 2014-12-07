#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2014                                              *  
#*   Daniel Falck <ddfalck@gmail.com>                                      *  
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


'''
This script requires that heekscnc be installed. Sorry, it's linux centric for now.
'''
import sys
sys.path.insert(0,'/usr/lib/heekscnc/')
from nc.nc import *
import nc.centroid1
import kurve_funcs
import area
area.set_units(25.4)

#######################################################
# drilling function
def drillholes(holeList,paramaters,keepdrilling=False):
    feedrate_hv(paramaters['verticalfeedrate'],paramaters['horizontalfeedrate'])
    #x, y = holeList
    z=0
    depth=paramaters['depth']
    standoff=paramaters['standoff']
    dwell=paramaters['dwell']
    peck_depth=paramaters['peck_depth']
    retract_mode=paramaters['retract_mode']
    spindle_mode=paramaters['spindle_mode']
    for i in holeList:
        x,y = i[0],i[1]
        drill(x, y, z, depth, standoff, dwell, peck_depth, retract_mode, spindle_mode)
    if keepdrilling:
        pass
    else:
        end_canned_cycle()

#######################################################
# profiling function

def profile(curve_name, profileparams,startparams):
    feedrate_hv(profileparams['verticalfeedrate'],profileparams['horizontalfeedrate'])
    side = profileparams['side']
    tool_diameter = profileparams['tooldiameter']
    offset_extra = profileparams['offset_extra']
    roll_radius = profileparams['roll_radius']
    roll_on = profileparams['roll_on']
    roll_off = profileparams['roll_off']
    rapid_safety_space = profileparams['rapid_safety_space']
    clearance = profileparams['clearance']
    start_depth = profileparams['start_depth']
    step_down = profileparams['step_down']
    final_depth = profileparams['final_depth']
    extend_at_start = profileparams['extend_at_start']
    extend_at_end = profileparams['extend_at_end']
    lead_in_line_len = profileparams['lead_in_line_len']
    lead_out_line_len = profileparams['lead_out_line_len']

    if startparams['startpt']:
        kurve_funcs.make_smaller( curve_name, start = area.Point(startparams['startptX'] ,startparams['startptY']))
    
    kurve_funcs.profile(curve_name, side, tool_diameter/2, offset_extra, roll_radius, roll_on, roll_off, rapid_safety_space, clearance, start_depth, step_down, final_depth,extend_at_start,extend_at_end,lead_in_line_len,lead_out_line_len )

#######################################################

# helical hole cutting

#use the next function for cutting out round holes -ie strap button holes
from math import fabs
def helical_hole(xPos, yPos, dia,  final_depth, clearance, step_down, step_over, tool_dia, start_depth):
    '''
    helical bore routine - no cutter comp
    '''
    if (tool_dia > dia):
        raise "tool wider than inner bore diameter"
 
    if (step_over > fabs(yPos+dia/2.0- tool_dia/2.0)):
        raise "step over too big"
    ydelta_plus = yPos + step_over  
    ydelta_minus = yPos - step_over   
    rapid(z=clearance)
    rapid(x=xPos,y=yPos-step_over )    
    currentDepth = start_depth-step_down
    arc_ccw(x=xPos,y=ydelta_plus,z=(start_depth),i=xPos,j=yPos)
    while currentDepth >= final_depth :       
        ydelta = 0.0
        ydelta_plus = yPos + step_over  
        ydelta_minus = yPos - step_over                  
        feed(y= ydelta_plus )
        yPos2 = yPos        
        arc_ccw(x=xPos,y=ydelta_minus,z=(currentDepth+step_down/2.0),i=xPos,j=yPos2)       
        arc_ccw(x=xPos,y=ydelta_plus,z=(currentDepth),i=xPos,j=yPos)
        while ydelta < ((dia/2.0 - tool_dia/2.0)-step_over):

            arc_ccw(x=xPos,y=ydelta_minus,i=xPos,j=yPos2)
            arc_ccw(x=xPos,y=ydelta_plus,i=xPos,j=yPos)
            temp = ydelta_plus
            ydelta= ydelta + step_over
            ydelta_plus= yPos  + ydelta +step_over
            ydelta_minus= yPos  - ydelta -step_over
            yPos2 = yPos-step_over/2.0
            
        midpoint = ((temp - (yPos-dia/2.0+ tool_dia/2.0))*.5) + (yPos-dia/2.0+ tool_dia/2.0)         
        arc_ccw(x=xPos,y=(yPos-dia/2.0+ tool_dia/2.0),i=xPos,j=midpoint)
        arc_ccw(x=xPos,y=(yPos+dia/2.0- tool_dia/2.0),i=xPos,j=yPos)
        arc_ccw(x=xPos,y=(yPos-dia/2.0+ tool_dia/2.0),i=xPos,j=yPos)        
        feed(xPos,yPos)        
        currentDepth = currentDepth - step_down
    ydelta = 0
    ydelta_plus = yPos + step_over  
    ydelta_minus = yPos - step_over 

    if currentDepth > final_depth :
        ydelta = 0.0
        ydelta_plus = yPos + step_over  
        ydelta_minus = yPos - step_over                  
        feed(y= ydelta_plus )
        yPos2 = yPos        
        arc_ccw(x=xPos,y=ydelta_minus,z=(final_depth+step_down/2.0),i=xPos,j=yPos2)       
        arc_ccw(x=xPos,y=ydelta_plus,z=(final_depth),i=xPos,j=yPos)
        while ydelta < ((dia/2.0 - tool_dia/2.0)-step_over):

            arc_ccw(x=xPos,y=ydelta_minus,i=xPos,j=yPos2)
            arc_ccw(x=xPos,y=ydelta_plus,i=xPos,j=yPos)
            temp = ydelta_plus
            ydelta= ydelta + step_over
            ydelta_plus= yPos  + ydelta +step_over

            ydelta_minus= yPos  - ydelta -step_over
            yPos2 = yPos-step_over/2.0           
        midpoint = ((temp - (yPos-dia/2.0+ tool_dia/2.0))*.5) + (yPos-dia/2.0+ tool_dia/2.0)         
        arc_ccw(x=xPos,y=(yPos-dia/2.0+ tool_dia/2.0),i=xPos,j=midpoint)
        arc_ccw(x=xPos,y=(yPos+dia/2.0- tool_dia/2.0),i=xPos,j=yPos)
        arc_ccw(x=xPos,y=(yPos-dia/2.0+ tool_dia/2.0),i=xPos,j=yPos)

    else:
        feed(xPos,yPos)      

    feed(xPos,yPos)        
    rapid(z=clearance)

#######################################################



