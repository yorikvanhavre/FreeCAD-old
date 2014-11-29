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

#include <strstream>
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
            std::string gcodestr = str.substr(last,found-last);
            Command *tmp = new Command();
            tmp->setFromGCode(gcodestr);
            vpcCommands.push_back(tmp);
        }
        last = found;
        found=str.find_first_of("gGmM",found+1);
    }
    // add the last command found, if any
    if (last > -1) {
        std::string gcodestr = str.substr(last,std::string::npos);
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
    // If the path is empty we simply store nothing. The file size will be 0 which
    // can be checked when reading in the data.
    if (toGCode().empty())
        return;
    // create a temporary file and copy the content to the zip stream
    // once the tmp. filename is known use always the same because otherwise
    // we may run into some problems on the Linux platform
    static Base::FileInfo fi(Base::FileInfo::getTempFileName());
    
    std::ofstream tfile;
    tfile.open(fi.filePath().c_str());
    if (tfile.fail()) {
        // Note: Do NOT throw an exception here because if the tmp. file could
        // not be created we should not abort.
        // We only print an error message but continue writing the next files to the
        // stream...
        throw Base::Exception("Error while saving Path data to file");
    } else {
        tfile << toGCode();
        tfile.close();
        
        Base::ifstream file(fi, std::ios::in | std::ios::binary);
        
        if (file){
            unsigned long ulSize = 0; 
            std::streambuf* buf = file.rdbuf();
            if (buf) {
                unsigned long ulCurr;
                ulCurr = buf->pubseekoff(0, std::ios::cur, std::ios::in);
                ulSize = buf->pubseekoff(0, std::ios::end, std::ios::in);
                buf->pubseekoff(ulCurr, std::ios::beg, std::ios::in);
            }
    
            // read in the ASCII file and write back to the stream
            std::strstreambuf sbuf(ulSize);
            file >> &sbuf;
            writer.Stream() << &sbuf;
        }
        file.close();
    }

    // remove temp file
    fi.deleteFile();
}

void Toolpath::Restore(XMLReader &reader)
{
    reader.readElement("Path");
    std::string file (reader.getAttribute("file") );

    if (!file.empty()) {
        // initate a file read
        reader.addFile(file.c_str(),this);
    }
}

void Toolpath::RestoreDocFile(Base::Reader &reader)
{
    // create a temporary file and copy the content from the zip stream
    Base::FileInfo fi(Base::FileInfo::getTempFileName());

    // read in the ASCII file and write back to the file stream
    Base::ofstream file(fi, std::ios::out | std::ios::binary);
    unsigned long ulSize = 0; 
    if (reader) {
        std::streambuf* buf = file.rdbuf();
        reader >> buf;
        file.flush();
        ulSize = buf->pubseekoff(0, std::ios::cur, std::ios::in);
    }
    file.close();

    // Read the path from the temp file, if the file is empty the stored path was already empty.
    // If it's still empty after reading the (non-empty) file there must occurred an error.
    if (ulSize > 0) {
        std::ifstream tfile(fi.filePath().c_str());
        if (tfile.fail()) {
            throw Base::Exception("Error reading Path data from file");
        } else {
            std::string gcode((std::istreambuf_iterator<char>(tfile)), std::istreambuf_iterator<char>());
            setFromGCode(gcode);
        }
    }

    // delete the temp file
    fi.deleteFile();
}




 
