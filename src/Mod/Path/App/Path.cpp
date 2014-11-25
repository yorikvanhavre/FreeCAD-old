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
#include <Base/Stream.h>
#include <Base/Exception.h>

#include "Path.h"

using namespace Path;
using namespace Base;

TYPESYSTEM_SOURCE(Path::Toolpath , Base::Persistence);

Toolpath::Toolpath()
{
}

Toolpath::Toolpath(const Toolpath& otherPath)
:vpcCommands(otherPath.vpcCommands.size())
{
    operator=(otherPath);
    recalculate();
}

Toolpath::~Toolpath()
{
    clear();
}

Toolpath &Toolpath::operator=(const Toolpath& otherPath)
{
    clear();
    vpcCommands.resize(otherPath.vpcCommands.size());
    int i = 0;
    for (std::vector<Command*>::const_iterator it=otherPath.vpcCommands.begin();it!=otherPath.vpcCommands.end();++it,i++)
        vpcCommands[i] = new Command(**it);
    recalculate();
    return *this;
}

void Toolpath::clear(void) 
{
    for(std::vector<Command*>::iterator it = vpcCommands.begin();it!=vpcCommands.end();++it)
        delete ( *it );
    vpcCommands.clear();
    recalculate();
}

void Toolpath::addCommand(const Command &Cmd)
{
    Command *tmp = new Command(Cmd);
    vpcCommands.push_back(tmp);
    recalculate();
}

void Toolpath::insertCommand(const Command &Cmd, int pos)
{
    if (pos == -1) {
        addCommand(Cmd);
    } else if (pos <= vpcCommands.size()) {
        Command *tmp = new Command(Cmd);
        vpcCommands.insert(vpcCommands.begin()+pos,tmp);
    } else {
        throw Base::Exception("Index not in range");
    }
    recalculate();
}

void Toolpath::deleteCommand(int pos)
{
    if (pos == -1) {
        //delete(*vpcCommands.rbegin()); // causes crash
        vpcCommands.pop_back();
    } else if (pos <= vpcCommands.size()) {
        vpcCommands.erase (vpcCommands.begin()+pos);
    } else {
        throw Base::Exception("Index not in range");
    }
    recalculate();
}

double Toolpath::getLength()
{
    double l = 0.0;
    if (!points.empty()) {
        Vector3d pos(0.,0.,0.);
        for(unsigned int i = 0;i<points.size(); i++) {
            Vector3d vec = *points[i];
            l += vec.Length();
            pos = pos + vec;
        }
    }
    return l;
}

void Toolpath::setFromGCode(const std::string str)
{
    clear();
    // split input string by G or M commands
    std::size_t found = str.find_first_of("gGmM");
    int last = -1;
    while (found!=std::string::npos)
    {
        if (last > -1) {
            std::string gcodestr = str.substr(last,found);
            Command *tmp = new Command();
            tmp->setFromGCode(gcodestr);
            vpcCommands.push_back(tmp);
        }
        last = found;
        found=str.find_first_of("gGmM",found+1);
    }
    // add the last command found, if any
    if (found != 0) {
        std::string gcodestr = str.substr(found,std::string::npos);
        Command *tmp = new Command();
        tmp->setFromGCode(gcodestr);
        vpcCommands.push_back(tmp);
    }
    recalculate();
}

std::string Toolpath::toGCode(void) const
{
    std::string result;
    for (std::vector<Command*>::const_iterator it=vpcCommands.begin();it!=vpcCommands.end();++it) {
        result += (*it)->toGCode();
        result += "\n";
    }
    return result;
}    

void Toolpath::recalculate(void) // recalculates the points cache
{
    //for(std::vector<Vector3d*>::iterator it = points.begin();it!=points.end();++it)
    //    delete ( *it ); // causes crash
    points.clear();
    //points.resize(vpcCommands.size()); // TODO later there might be more points than commands (ie. arcs)
    for (std::vector<Command*>::const_iterator it=vpcCommands.begin();it!=vpcCommands.end();++it) {
        Vector3d *pos = new Vector3d((*it)->getPlacement().getPosition());
        points.push_back(pos);
    }
}

// reimplemented from base class

unsigned int Toolpath::getMemSize (void) const
{
    return toGCode().size();
}

void Toolpath::Save (Writer &writer) const
{
    if (writer.isForceXML()) {
        writer.Stream() << writer.ind() << "<Path count=\"" <<  getSize() <<"\">" << std::endl;
        writer.incInd();
        for(unsigned int i = 0;i<getSize(); i++)
            vpcCommands[i]->Save(writer);
        writer.decInd();
        writer.Stream() << writer.ind() << "</Path>" << std::endl;
    } else {
        writer.Stream() << writer.ind()
            << "<Path file=\"" << writer.addFile((writer.ObjectName+".nc").c_str(), this) << "\"/>" << std::endl;
    }
}

void Toolpath::SaveDocFile (Base::Writer &writer) const
{
    // TODO doesn't work
    Base::OutputStream str(writer.Stream());
    const uint8_t* sbuffer = (uint8_t*) toGCode().c_str();
    str << sbuffer;
}

void Toolpath::Restore(XMLReader &reader)
{
    clear();
    // read my element
    reader.readElement("Path");
    std::string file (reader.getAttribute("file") );
    if(file == "") {
        // XML data
        int count = reader.getAttributeAsInteger("count");
        vpcCommands.resize(count);
        for (int i = 0; i < count; i++) {
            Command *tmp = new Command();
            tmp->Restore(reader);
            vpcCommands[i] = tmp;
        }
    } else {
        reader.addFile(file.c_str(),this);
    }
    recalculate();
}

void Toolpath::RestoreDocFile(Base::Reader &reader)
{
    // TODO doesn't work
    Base::InputStream str(reader);
    uint8_t sbuffer;
    str >> sbuffer;
    std::string gcode(reinterpret_cast<const char *>(sbuffer));
    setFromGCode(gcode);
}




 
