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

#include "FeaturePathProject.h"
#include "FeaturePathCompound.h"
#include "Tooltable.h"

using namespace Path;
using namespace App;

PROPERTY_SOURCE(Path::FeatureProject, Path::FeatureCompound)


FeatureProject::FeatureProject()
{
    ADD_PROPERTY_TYPE( Tooltable,   (Path::Tooltable()), "Machine",App::Prop_None,"The tooltable of this feature");
//    ADD_PROPERTY_TYPE( Fixtures,    ((Base::Vector3d())),"Machine",App::Prop_None,"The list of fixtures points of this feature");
    ADD_PROPERTY_TYPE( CornerMin,   (Base::Vector3d()),  "Machine",App::Prop_None,"The lower left corner of the machine extents");
    ADD_PROPERTY_TYPE( CornerMax,   (Base::Vector3d()),  "Machine",App::Prop_None,"The upper right corner of the machine extents");
    ADD_PROPERTY_TYPE( SafeHeight,  (0),                 "Machine",App::Prop_None,"The safe height of this machine setup");
    ADD_PROPERTY_TYPE( Description, (""),                "Machine",App::Prop_None,"An optional description of this CNC Project");
//    ADD_PROPERTY_TYPE( FeedRate,    (0),                 "Machine",App::Prop_None,"The default feed rate of this machine");
//    ADD_PROPERTY_TYPE( SpindleSpeed,(0),                 "Machine",App::Prop_None,"The default spindle speed of this machine");

}

FeatureProject::~FeatureProject()
{
}
