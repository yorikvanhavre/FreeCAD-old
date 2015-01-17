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


#ifndef PATH_FeatureProject_H
#define PATH_FeatureProject_H

#include "FeaturePathCompound.h"
#include "PropertyTooltable.h"
#include <App/PropertyUnits.h>

namespace Path
{

class PathExport FeatureProject : public Path::FeatureCompound
{
    PROPERTY_HEADER(Path::FeatureCompound);

public:
    /// Constructor
    FeatureProject(void);
    virtual ~FeatureProject();

    Path::PropertyTooltable   Tooltable;
//    App::PropertyVectorList   Fixtures;
    App::PropertyVector       CornerMin;
    App::PropertyVector       CornerMax;
    App::PropertyLength       SafeHeight;
    App::PropertyString       Description;
//    App::PropertySpeed        FeedRate;
//    App::PropertyFloat        SpindleSpeed;


    /// returns the type name of the ViewProvider
    virtual const char* getViewProviderName(void) const {
        return "PathGui::ViewProviderPathProject";
    }
};

} //namespace Path


#endif // PATH_FeatureProject_H
