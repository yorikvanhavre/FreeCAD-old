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
#include <App/Application.h>
#include <App/Document.h>
#include <Base/FileInfo.h>
#include <Base/Stream.h>
#include <Base/Console.h>
#include <Base/Parameter.h>
#include <Gui/BitmapFactory.h>

using namespace Gui;
using namespace PathGui;
using namespace Path;

PROPERTY_SOURCE(PathGui::ViewProviderPath, Gui::ViewProviderGeometryObject)

ViewProviderPath::ViewProviderPath()
{
    ParameterGrp::handle hGrp = App::GetApplication().GetParameterGroupByPath("User parameter:BaseApp/Preferences/Mod/Path");
    unsigned long lcol = hGrp->GetUnsigned("DefaultNormalPathColor",11141375UL); // dark green (0,170,0)
    float lr,lg,lb;
    lr = ((lcol >> 24) & 0xff) / 255.0; lg = ((lcol >> 16) & 0xff) / 255.0; lb = ((lcol >> 8) & 0xff) / 255.0;
    unsigned long rcol = hGrp->GetUnsigned("DefaultRapidPathColor",2852126975UL); // dark red (170,0,0)
    float rr,rg,rb;
    rr = ((rcol >> 24) & 0xff) / 255.0; rg = ((rcol >> 16) & 0xff) / 255.0; rb = ((rcol >> 8) & 0xff) / 255.0;
    unsigned long mcol = hGrp->GetUnsigned("DefaultPathMarkerColor",1442775295UL); // lime green (85,255,0)
    float mr,mg,mb;
    mr = ((mcol >> 24) & 0xff) / 255.0; mg = ((mcol >> 16) & 0xff) / 255.0; mb = ((mcol >> 8) & 0xff) / 255.0;
    int lwidth = hGrp->GetInt("DefaultPathLineWidth",1);
    ADD_PROPERTY(NormalColor,(lr,lg,lb));
    ADD_PROPERTY(RapidColor,(rr,rg,rb));
    ADD_PROPERTY(MarkerColor,(mr,mg,mb));
    ADD_PROPERTY(LineWidth,(lwidth));
    
    pcPathRoot = new Gui::SoFCSelection();
    pcPathRoot->highlightMode = Gui::SoFCSelection::ON;
    pcPathRoot->selectionMode = Gui::SoFCSelection::SEL_ON;
    pcPathRoot->ref();

    pcLineCoords = new SoCoordinate3();
    pcLineCoords->ref();

    pcMarkerCoords = new SoCoordinate3();
    pcMarkerCoords->ref();
    
    pcDrawStyle = new SoDrawStyle();
    pcDrawStyle->ref();
    pcDrawStyle->style = SoDrawStyle::LINES;
    pcDrawStyle->lineWidth = LineWidth.getValue();

    pcLines = new SoLineSet;
    pcLines->ref();
    
    pcLineColor = new SoBaseColor;
    pcLineColor->ref();
    
    pcMarkerColor = new SoBaseColor;
    pcMarkerColor->ref();
    
    NormalColor.touch();
    RapidColor.touch();
    MarkerColor.touch();
}

ViewProviderPath::~ViewProviderPath()
{
    pcPathRoot->unref();
    pcLineCoords->unref();
    pcMarkerCoords->unref();
    pcDrawStyle->unref();
    pcLines->unref();
    pcLineColor->unref();
    pcMarkerColor->unref();
}

void ViewProviderPath::attach(App::DocumentObject *pcObj)
{
    ViewProviderDocumentObject::attach(pcObj);

    // Draw trajectory lines
    SoSeparator* linesep = new SoSeparator;
    linesep->addChild(pcLineColor);
    linesep->addChild(pcDrawStyle);
    linesep->addChild(pcLineCoords);
    linesep->addChild(pcLines);

    // Draw markers
    SoSeparator* markersep = new SoSeparator;
    SoMarkerSet* marker = new SoMarkerSet;
    marker->markerIndex=SoMarkerSet::CROSS_5_5;
    markersep->addChild(pcMarkerColor);
    markersep->addChild(pcMarkerCoords);
    markersep->addChild(marker);

    pcPathRoot->addChild(linesep);
    pcPathRoot->addChild(markersep);

    addDisplayMaskMode(pcPathRoot, "Waypoints");
    pcPathRoot->objectName = pcObj->getNameInDocument();
    pcPathRoot->documentName = pcObj->getDocument()->getName();
    pcPathRoot->subElementName = "Path";
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

void ViewProviderPath::onChanged(const App::Property* prop)
{
    if (prop == &LineWidth) {
        pcDrawStyle->lineWidth = LineWidth.getValue();
    } else if (prop == &NormalColor) {
        const App::Color& c = NormalColor.getValue();
        pcLineColor->rgb.setValue(c.r,c.g,c.b);
    } else if (prop == &MarkerColor) {
        const App::Color& c = MarkerColor.getValue();
        pcMarkerColor->rgb.setValue(c.r,c.g,c.b);
    } else {
        ViewProviderGeometryObject::onChanged(prop);
    }
}

void ViewProviderPath::updateData(const App::Property* prop)
{
    Path::Feature* pcPathObj = static_cast<Path::Feature*>(pcObject);

    if ( (prop == &pcPathObj->Path) || (prop == &pcPathObj->Placement) ) {
        
        const Toolpath &tp = pcPathObj->Path.getValue();
        if(tp.getSize()==0)
            return;
            
        ParameterGrp::handle hGrp = App::GetApplication().GetParameterGroupByPath("User parameter:BaseApp/Preferences/Mod/Part");
        float deviation = hGrp->GetFloat("MeshDeviation",0.2);
        Base::Placement loc = *(&pcPathObj->Placement.getValue());
        std::vector<Base::Vector3d> points;
        std::vector<Base::Vector3d> markers;
        Base::Vector3d last(loc.getPosition());
        points.push_back(last);
        markers.push_back(last);
        
        for (int  i = 0; i < tp.getSize(); i++) {
            Path::Command cmd = tp.getCommand(i);
            std::string name = cmd.Name;
            Base::Vector3d pt = cmd.getPlacement().getPosition();
            if (!cmd.has("z"))
                pt.z = last.z;
            Base::Vector3d next;
            loc.multVec(pt,next);
            
            if ( (name == "G0") || (name == "G1") || (name == "G01") ) {
                // straight line
                points.push_back(next);
                markers.push_back(next);
                last = next;
                
            } else if ( (name == "G2") || (name == "G02") || (name == "G3") || (name == "G03") ) {
                // arc
                Base::Vector3d norm, zaxis;
                if ( (name == "G2") || (name == "G02") )
                    zaxis.Set(0,0,-1);
                else
                    zaxis.Set(0,0,1);
                loc.getRotation().multVec(zaxis,norm);
                Base::Vector3d ce = (last + cmd.getCenter());
                Base::Vector3d center;
                loc.multVec(ce,center);
                double radius = (last - center).Length();
                double angle = (next - center).GetAngle(last - center);
                int segments = 2/deviation; //we use a rather simple rule here, provisorily
                for (int j = 1; j < segments; j++) {
                    //std::cout << "vector " << j << std::endl;
                    Base::Vector3d inter;
                    Base::Rotation rot(norm,(angle/segments)*j);
                    //std::cout << "angle " << (angle/segments)*j << std::endl;
                    rot.multVec((last - center),inter);
                    //std::cout << "result " << inter.x << " , " << inter.y << " , " << inter.z << std::endl;
                    points.push_back( center + inter);
                }
                //std::cout << "next " << next.x << " , " << next.y << " , " << next.z << std::endl;
                points.push_back(next);
                markers.push_back(next);
                markers.push_back(center); // add a marker at center too, why not?
                last = next;
            }
        }
        
        pcLineCoords->point.deleteValues(0);
        pcLineCoords->point.setNum(points.size());
        for(unsigned int i=0;i<points.size();i++)
            pcLineCoords->point.set1Value(i,points[i].x,points[i].y,points[i].z);
        pcLines->numVertices.set1Value(0, points.size());

        pcMarkerCoords->point.deleteValues(0);
        pcMarkerCoords->point.setNum(markers.size());
        for(unsigned int i=0;i<markers.size();i++)
            pcMarkerCoords->point.set1Value(i,markers[i].x,markers[i].y,markers[i].z);
    }
}

QIcon ViewProviderPath::getIcon() const
{
    return Gui::BitmapFactory().pixmap("Path-Toolpath");
}

