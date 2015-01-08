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

#include "ViewProviderPathProject.h"
#include <Mod/Path/App/FeaturePathProject.h>
#include <Mod/Path/App/FeaturePathCompound.h>
#include <App/Application.h>
#include <Gui/BitmapFactory.h>
#include <Gui/SoFCBoundingBox.h>
#include <Inventor/nodes/SoSeparator.h>
#include <Inventor/nodes/SoDrawStyle.h>
#include <Inventor/nodes/SoBaseColor.h>

using namespace Gui;
using namespace PathGui;

PROPERTY_SOURCE(PathGui::ViewProviderPathProject, PathGui::ViewProviderPathCompound)

ViewProviderPathProject::ViewProviderPathProject()
{
    ADD_PROPERTY_TYPE(ShowExtents,(false),"Path",(App::PropertyType)(App::Prop_None),"Switch the machine extents bounding box on/off");
    ExtentsRoot = new SoSeparator();
    ExtentsRoot->ref();
    pcPathRoot->addChild(ExtentsRoot);
}

ViewProviderPathProject::~ViewProviderPathProject()
{
    ExtentsRoot->unref();
}

void ViewProviderPathProject::showExtents(void)
{
    std::cout << "show extents" << std::endl;
    // first create an uncomputable group
    SoGroup *parent = new Gui::SoSkipBoundingGroup();
    ExtentsRoot->removeAllChildren();
    ExtentsRoot->addChild(parent);
    
    // add a dashed style
    ParameterGrp::handle hGrp = App::GetApplication().GetParameterGroupByPath("User parameter:BaseApp/Preferences/Mod/Part");
    int pattern = hGrp->GetInt("GridLinePattern", 0x0f0f);
    SoDrawStyle* DefaultStyle = new SoDrawStyle;
    DefaultStyle->lineWidth = 1;
    DefaultStyle->linePattern = pattern;
    parent->addChild(DefaultStyle);
    
    // add a color
    ParameterGrp::handle hGrp2 = App::GetApplication().GetParameterGroupByPath("User parameter:BaseApp/Preferences/Mod/Path");
    unsigned long col = hGrp2->GetUnsigned("DefaultExtentsColor",3418866943UL); // light grey (203,199,196)
    float r,g,b;
    r = ((col >> 24) & 0xff) / 255.0; g = ((col >> 16) & 0xff) / 255.0; b = ((col >> 8) & 0xff) / 255.0;
    SoBaseColor *ecolor = new SoBaseColor;
    ecolor->rgb.setValue(r,g,b);
    parent->addChild(ecolor);

    // add a bounding box
    Gui::SoFCBoundingBox* extents = new Gui::SoFCBoundingBox();
    extents->coordsOn.setValue(false);
    extents->dimensionsOn.setValue(true);
    Path::FeatureProject* pcPathObj = static_cast<Path::FeatureProject*>(pcObject);
    Base::Vector3d p1 = *(&pcPathObj->CornerMin.getValue());
    Base::Vector3d p2 = *(&pcPathObj->CornerMax.getValue());
    extents->minBounds.setValue(p1.x, p1.y, p1.z);
    extents->maxBounds.setValue(p2.x, p2.y, p2.z);
    parent->addChild(extents);
}

void ViewProviderPathProject::onChanged(const App::Property* prop)
{
    // call father
    ViewProviderPathCompound::onChanged(prop);

    if (prop == &ShowExtents) {
        if (ShowExtents.getValue())
            showExtents();
        else
            ExtentsRoot->removeAllChildren();
    }
}

void ViewProviderPathProject::attach(App::DocumentObject *pcFeat)
{
    ViewProviderPathCompound::attach(pcFeat);

    if (ShowExtents.getValue())
        showExtents();
}

QIcon ViewProviderPathProject::getIcon() const
{
    return Gui::BitmapFactory().pixmap("Path-Project");
}
