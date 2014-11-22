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

#include "Path.h"

using namespace Path;
using namespace Base;

TYPESYSTEM_SOURCE(Path::Toolpath , Base::Persistence);

Toolpath::Toolpath()
{
}

Toolpath::Toolpath(const Toolpath& otherPath)
:vpcCommands(otherPath.vpcCommands.size()),points(otherPath.points.size())
{
    operator=(otherPath);
}

Toolpath::~Toolpath()
{
    for(std::vector<Command*>::iterator it = vpcCommands.begin();it!=vpcCommands.end();++it)
        delete ( *it );
    for(std::vector<Vector3d*>::iterator it = points.begin();it!=points.end();++it)
        delete ( *it );
}

Toolpath &Toolpath::operator=(const Toolpath& otherPath)
{
    for(std::vector<Command*>::iterator it = vpcCommands.begin();it!=vpcCommands.end();++it)
        delete ( *it );
    vpcCommands.clear();
    vpcCommands.resize(otherPath.vpcCommands.size());
    int i = 0;
    for (std::vector<Command*>::const_iterator it=otherPath.vpcCommands.begin();it!=otherPath.vpcCommands.end();++it,i++)
        vpcCommands[i] = new Command(**it);
        
    for(std::vector<Vector3d*>::iterator it = points.begin();it!=points.end();++it)
        delete ( *it );
    points.clear();
    points.resize(otherPath.points.size());
    i = 0;
    for (std::vector<Vector3d*>::const_iterator it=otherPath.points.begin();it!=otherPath.points.end();++it,i++)
        points[i] = new Vector3d(**it);
        
    return *this;
}

void Toolpath::addCommand(const Command &Cmd)
{
    Command *tmp = new Command(Cmd);
    vpcCommands.push_back(tmp);
    Vector3d *pos = new Vector3d(tmp->getPlacement().getPosition());
    points.push_back(pos);
}

double Toolpath::getLength()
{
    double l = 0.0;
    if (!vpcCommands.empty()) {
        Vector3d pos(0.,0.,0.);
        for(unsigned int i = 0;i<getSize(); i++) {
            Vector3d vec = *points[i];
            l += vec.Length();
            pos = pos + vec;
        }
    }
    return l;
}

unsigned int Toolpath::getMemSize (void) const
{
    return 0;
}

void Toolpath::Save (Writer &writer) const
{
    writer.Stream() << writer.ind() << "<Path count=\"" <<  getSize() <<"\">" << std::endl;
    writer.incInd();
    for(unsigned int i = 0;i<getSize(); i++)
        vpcCommands[i]->Save(writer);
    writer.decInd();
    writer.Stream() << writer.ind() << "</Path>" << std::endl ;

}

void Toolpath::Restore(XMLReader &reader)
{
    vpcCommands.clear();
    // read my element
    reader.readElement("Path");
    // get the value of my Attribute
    int count = reader.getAttributeAsInteger("count");
    vpcCommands.resize(count);

    for (int i = 0; i < count; i++) {
        Command *tmp = new Command();
        tmp->Restore(reader);
        vpcCommands[i] = tmp;
    }
}




 
