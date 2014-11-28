/***************************************************************************
 *   Copyright (c) Yorik van Havre (yorik@uncreated.net) 2014              *
 *                                                                         *
 *   This file is part of the FreeCAD CAx development system.              *
 *                                                                         *
 *   This library is free software; you can redistribute it and/or         *
 *   modify it under the terms of the GNU Library General Public           *
 *   License as published by the Free Software Foundation; either          *
 *   version 2 of the License, or (at your option) any later version.      *
 *                                                                         *
 *   This library  is distributed in the hope that it will be useful,      *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU Library General Public License for more details.                  *
 *                                                                         *
 *   You should have received a copy of the GNU Library General Public     *
 *   License along with this library; see the file COPYING.LIB. If not,    *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,         *
 *   Suite 330, Boston, MA  02111-1307, USA                                *
 *                                                                         *
 ***************************************************************************/


#include "PreCompiled.h"

#ifndef _PreComp_

#endif
#include <Base/Writer.h>
#include <Base/Reader.h>
#include <Base/Exception.h>
#include "Tooltable.h"

using namespace Base;
using namespace Path;


// TOOL


TYPESYSTEM_SOURCE(Path::Tool , Base::Persistence);

// Constructors & destructors

Tool::Tool(const char* name,
           ToolType type,
           ToolMaterial material,
           double diameter, 
           double lengthoffset,
           double flatradius,
           double cornerradius,
           double cuttingedgeangle,
           double cuttingedgeheight)
:Name(name),Type(type),Diameter(diameter),LengthOffset(lengthoffset),
FlatRadius(flatradius),CornerRadius(cornerradius),CuttingEdgeAngle(cuttingedgeangle),
CuttingEdgeHeight(cuttingedgeheight)
{
}

Tool::Tool()
{
}

Tool::~Tool()
{
}

// Reimplemented from base class

unsigned int Tool::getMemSize (void) const
{
    return 0;
}

void Tool::Save (Writer &writer) const
{
    writer.Stream() << writer.ind() << "<Tool "
                    << "name=\"" << Name << "\" " 
                    << "diameter=\"" << Diameter << "\" "
                    << "length=\"" << LengthOffset << "\" "
                    << "flat=\"" <<  FlatRadius << "\" "
                    << "corner=\"" << CornerRadius << "\" "
                    << "angle=\"" << CuttingEdgeAngle << "\" "
                    << "height=\"" << CuttingEdgeHeight << "\" ";
                    
    if(Type == Tool::ENDMILL)
        writer.Stream() << " type=\"EndMill\" ";
    else if(Type == Tool::DRILL)
        writer.Stream() << " type=\"Drill\" ";
    else if(Type == Tool::CENTERDRILL)
        writer.Stream() << " type=\"CenterDrill\" ";
    else if(Type == Tool::COUNTERSINK)
        writer.Stream() << " type=\"CounterSink\" ";
    else if(Type == Tool::COUNTERBORE)
        writer.Stream() << " type=\"CounterBore\" ";
    else if(Type == Tool::REAMER)
        writer.Stream() << " type=\"Reamer\" ";
    else if(Type == Tool::TAP)
        writer.Stream() << " type=\"Tap\" ";
    else if(Type == Tool::SLOTCUTTER)
        writer.Stream() << " type=\"SlotCutter\" ";
    else if(Type == Tool::BALLENDMILL)
        writer.Stream() << " type=\"BallEndMill\" ";
    else if(Type == Tool::CHAMFERMILL)
        writer.Stream() << " type=\"ChamferMill\" ";
    else if(Type == Tool::CORNERROUND)
        writer.Stream() << " type=\"CornerRound\" ";
    else if(Type == Tool::ENGRAVER)
        writer.Stream() << " type=\"Engraver\" ";
    else
        writer.Stream() << " type=\"Undefined\" ";
        
    if(Material == Tool::CARBIDE)
        writer.Stream() << " mat=\"Carbide\" /> ";
    else if(Material == Tool::HIGHSPEEDSTEEL)
        writer.Stream() << " mat=\"HighSpeedSteel\" /> ";
    else if(Material == Tool::HIGHCARBONTOOLSTEEL)
        writer.Stream() << " mat=\"HighCarbonToolSteel\" /> ";
    else if(Material == Tool::CASTALLOY)
        writer.Stream() << " mat=\"CastAlloy\" /> ";
    else if(Material == Tool::CERAMICS)
        writer.Stream() << " mat=\"Ceramics\" /> ";
    else if(Material == Tool::DIAMOND)
        writer.Stream() << " mat=\"Diamond\" /> ";
    else if(Material == Tool::SIALON)
        writer.Stream() << " mat=\"Sialon\" /> ";
    else
        writer.Stream() << " mat=\"Undefined\" /> ";
    writer.Stream()<< std::endl;
}

void Tool::Restore(XMLReader &reader)
{
    reader.readElement("Tool");
    Name = reader.getAttribute("name");
    Diameter = (double) reader.getAttributeAsFloat("diameter");
    LengthOffset = (double) reader.getAttributeAsFloat("length");
    FlatRadius = (double) reader.getAttributeAsFloat("flat");
    CornerRadius = (double) reader.getAttributeAsFloat("corner");
    CuttingEdgeAngle = (double) reader.getAttributeAsFloat("angle");
    CuttingEdgeHeight = (double) reader.getAttributeAsFloat("height");
    
    std::string type = reader.getAttribute("type");
    if(type=="EndMill")
        Type = Tool::ENDMILL;
    else if(type=="Drill")
        Type = Tool::DRILL;
    else if(type=="CenterDrill")
        Type = Tool::CENTERDRILL;
    else if(type=="CounterSink")
        Type = Tool::COUNTERSINK;
    else if(type=="CounterBore")
        Type = Tool::COUNTERBORE;
    else if(type=="Reamer")
        Type = Tool::REAMER;
    else if(type=="Tap")
        Type = Tool::TAP;
    else if(type=="SlotCutter")
        Type = Tool::SLOTCUTTER;
    else if(type=="BallEndMill")
        Type = Tool::BALLENDMILL;
    else if(type=="ChamferMill")
        Type = Tool::CHAMFERMILL;
    else if(type=="CornerRound")
        Type = Tool::CORNERROUND;
    else if(type=="Engraver")
        Type = Tool::ENGRAVER;
    else 
        Type = Tool::UNDEFINED;
        
    std::string mat = reader.getAttribute("mat");
    if(mat=="Carbide")
        Material = Tool::CARBIDE;
    else if(mat=="HighSpeedSteel")
        Material = Tool::HIGHSPEEDSTEEL;
    else if(mat=="HighCarbonToolSteel")
        Material = Tool::HIGHCARBONTOOLSTEEL;
    else if(mat=="CastAlloy")
        Material = Tool::CASTALLOY;
    else if(mat=="Ceramics")
        Material = Tool::CERAMICS;
    else if(mat=="Diamond")
        Material = Tool::DIAMOND;
    else if(mat=="Sialon")
        Material = Tool::SIALON;
    else
        Material = Tool::MATUNDEFINED;
}



// TOOLTABLE



TYPESYSTEM_SOURCE(Path::Tooltable , Base::Persistence);

Tooltable::Tooltable()
{
}

Tooltable::~Tooltable()
{
}

void Tooltable::addTool(const Tool &tool)
{
    Tool *tmp = new Tool(tool);
    Tools.push_back(tmp);
}

void Tooltable::insertTool(const Tool &tool, int pos)
{
    if (pos == -1) {
        addTool(tool);
    } else if (pos <= Tools.size()) {
        Tool *tmp = new Tool(tool);
        Tools.insert(Tools.begin()+pos,tmp);
    } else {
        throw Base::Exception("Index not in range");
    }
}

void Tooltable::deleteTool(int pos)
{
    if (pos == -1) {
        Tools.pop_back();
    } else if (pos <= Tools.size()) {
        Tools.erase (Tools.begin()+pos);
    } else {
        throw Base::Exception("Index not in range");
    }
}

unsigned int Tooltable::getMemSize (void) const
{
    return 0;
}

void Tooltable::Save (Writer &writer) const
{
    writer.Stream() << writer.ind() << "<Tooltable count=\"" <<  getSize() <<"\">" << std::endl;
    writer.incInd();
    for(unsigned int i = 0;i<getSize(); i++)
        Tools[i]->Save(writer);
    writer.decInd();
    writer.Stream() << writer.ind() << "</Tooltable>" << std::endl ;

}

void Tooltable::Restore(XMLReader &reader)
{
    Tools.clear();
    reader.readElement("Tooltable");
    int count = reader.getAttributeAsInteger("count");
    Tools.resize(count);
    for (int i = 0; i < count; i++) {
        Tool *tmp = new Tool();
        tmp->Restore(reader);
        Tools[i] = tmp;
    }
}




