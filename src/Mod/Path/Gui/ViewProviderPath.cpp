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
# include <Inventor/SoDB.h>
# include <Inventor/SoInput.h>
# include <Inventor/SbVec3f.h>
# include <Inventor/nodes/SoSeparator.h>
# include <Inventor/nodes/SoTransform.h>
# include <Inventor/nodes/SoSphere.h>
# include <Inventor/nodes/SoRotation.h>
# include <Inventor/actions/SoSearchAction.h>
# include <Inventor/draggers/SoJackDragger.h>
# include <Inventor/nodes/SoBaseColor.h>
# include <Inventor/nodes/SoCoordinate3.h>
# include <Inventor/nodes/SoDrawStyle.h>
# include <Inventor/nodes/SoFaceSet.h>
# include <Inventor/nodes/SoLineSet.h>
# include <Inventor/nodes/SoMarkerSet.h>
# include <Inventor/nodes/SoShapeHints.h>
# include <QFile>
#endif

#include "ViewProviderPath.h"

#include <Mod/Path/App/FeaturePath.h>
#include <Mod/Path/App/Path.h>
#include <App/Document.h>
#include <Base/FileInfo.h>
#include <Base/Stream.h>
#include <Base/Console.h>
#include <sstream>

using namespace Gui;
using namespace PathGui;
using namespace Path;

PROPERTY_SOURCE(PathGui::ViewProviderPath, Gui::ViewProviderGeometryObject)

ViewProviderPath::ViewProviderPath()
{
    pcPathRoot = new Gui::SoFCSelection();
    pcPathRoot->highlightMode = Gui::SoFCSelection::OFF;
    pcPathRoot->selectionMode = Gui::SoFCSelection::SEL_OFF;
    pcPathRoot->ref();

    pcCoords = new SoCoordinate3();
    pcCoords->ref();
    
    pcDrawStyle = new SoDrawStyle();
    pcDrawStyle->ref();
    pcDrawStyle->style = SoDrawStyle::LINES;
    pcDrawStyle->lineWidth = 2;

    pcLines = new SoLineSet;
    pcLines->ref();
}

ViewProviderPath::~ViewProviderPath()
{
    pcPathRoot->unref();
    pcCoords->unref();
    pcDrawStyle->unref();
    pcLines->unref();
}

void ViewProviderPath::attach(App::DocumentObject *pcObj)
{
    ViewProviderDocumentObject::attach(pcObj);

    // Draw trajectory lines
    SoSeparator* linesep = new SoSeparator;
    SoBaseColor * basecol = new SoBaseColor;
    basecol->rgb.setValue( 1.0f, 0.5f, 0.0f );
    linesep->addChild(basecol);
    linesep->addChild(pcCoords);
    linesep->addChild(pcLines);

    // Draw markers
    SoBaseColor * markcol = new SoBaseColor;
    markcol->rgb.setValue( 1.0f, 1.0f, 0.0f );
    SoMarkerSet* marker = new SoMarkerSet;
    marker->markerIndex=SoMarkerSet::CROSS_5_5;
    linesep->addChild(markcol);
    linesep->addChild(marker);

    pcPathRoot->addChild(linesep);

    addDisplayMaskMode(pcPathRoot, "Waypoints");
    pcPathRoot->objectName = pcObj->getNameInDocument();
    pcPathRoot->documentName = pcObj->getDocument()->getName();
    pcPathRoot->subElementName = "Main";
}

void ViewProviderPath::setDisplayMode(const char* ModeName)
{
    if ( strcmp("Waypoints",ModeName)==0 )
        setDisplayMaskMode("Waypoints");
    ViewProviderGeometryObject::setDisplayMode( ModeName );
}

std::vector<std::string> ViewProviderPath::getDisplayModes(void) const
{
    std::vector<std::string> StrList;
    StrList.push_back("Waypoints");
    return StrList;
}

void ViewProviderPath::updateData(const App::Property* prop)
{
    Path::Feature* pcPathObj = static_cast<Path::Feature*>(pcObject);
    /*
    if (prop == &pcPathObj->Path) {
        const Toolpath &trak = pcPathObj->Path.getValue();

        pcCoords->point.deleteValues(0);
        pcCoords->point.setNum(trak.getSize());

        for(unsigned int i=0;i<trak.getSize();++i){
            Base::Vector3d pos = trak.getCommand(i).getPoint();
            pcCoords->point.set1Value(i,pos.x,pos.y,pos.z);
        }
        pcLines->numVertices.set1Value(0, trak.getSize());
    }else if (prop == &pcTracObj->Base) {
        Base::Placement loc = *(&pcTracObj->Base.getValue());
    }
    */
}

