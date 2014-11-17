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


#ifndef PATH_Path_H
#define PATH_Path_H

#include "Command.h"

#include <Base/Persistence.h>

namespace Path
{

    /** The representation of a CNC Toolpath */
    
    class PathExport Toolpath : public Base::Persistence
    {
        TYPESYSTEM_HEADER();
    
        public:
            Toolpath();
            Toolpath(const Toolpath&);
            ~Toolpath();
            
            Toolpath &operator=(const Toolpath&);
        
            // from base class
            virtual unsigned int getMemSize (void) const;
            virtual void Save (Base::Writer &/*writer*/) const;
            virtual void Restore(Base::XMLReader &/*reader*/);
        
            // interface
            void addCommand(const Command &Cmd);
            unsigned int getSize(void) const{return vpcCommands.size();}
            const Command &getCommand(unsigned int pos)const {return *vpcCommands[pos];}
            const std::vector<Command*> &getCommands(void)const{return vpcCommands;}
            double getLength(void); // return the Length (mm) of the Path
        
        protected:
            std::vector<Command*> vpcCommands;
    };

} //namespace Path


#endif // PATH_Path_H
