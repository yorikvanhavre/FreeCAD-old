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
# include <Inventor/SbVec3f.h>
# include <Inventor/nodes/SoSeparator.h>
# include <Inventor/nodes/SoTransform.h>
# include <Inventor/nodes/SoRotation.h>
# include <Inventor/nodes/SoBaseColor.h>
# include <Inventor/nodes/SoMaterial.h>
# include <Inventor/nodes/SoMaterialBinding.h>
# include <Inventor/nodes/SoCoordinate3.h>
# include <Inventor/nodes/SoDrawStyle.h>
# include <Inventor/nodes/SoIndexedLineSet.h>
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
    unsigned long mcol = hGrp->GetUnsigned("DefaultPathMarkerColor",1442775295UL); // lime green (85,255,0)
    float mr,mg,mb;
    mr = ((mcol >> 24) & 0xff) / 255.0; mg = ((mcol >> 16) & 0xff) / 255.0; mb = ((mcol >> 8) & 0xff) / 255.0;
    int lwidth = hGrp->GetInt("DefaultPathLineWidth",1);
    ADD_PROPERTY(NormalColor,(lr,lg,lb));
    ADD_PROPERTY(MarkerColor,(mr,mg,mb));
    ADD_PROPERTY(LineWidth,(lwidth));
    
    pcPathRoot = new Gui::SoFCSelection();

    pcPathRoot->style = Gui::SoFCSelection::EMISSIVE;
    pcPathRoot->highlightMode = Gui::SoFCSelection::AUTO;
    pcPathRoot->selectionMode = Gui::SoFCSelection::SEL_ON;
    pcPathRoot->ref();
    
    pcTransform = new SoTransform();
    pcTransform->ref();

    pcLineCoords = new SoCoordinate3();
    pcLineCoords->ref();

    pcMarkerCoords = new SoCoordinate3();
    pcMarkerCoords->ref();
    
    pcDrawStyle = new SoDrawStyle();
    pcDrawStyle->ref();
    pcDrawStyle->style = SoDrawStyle::LINES;
    pcDrawStyle->lineWidth = LineWidth.getValue();

    pcLines = new SoIndexedLineSet;
    pcLines->ref();
    
    pcLineColor = new SoMaterial;
    pcLineColor->ref();
    
    pcMatBind = new SoMaterialBinding;
    pcMatBind->ref();
    pcMatBind->value = SoMaterialBinding::OVERALL;

    pcMarkerColor = new SoBaseColor;
    pcMarkerColor->ref();
    
    NormalColor.touch();
    MarkerColor.touch();
}

ViewProviderPath::~ViewProviderPath()
{
    pcPathRoot->unref();
    pcTransform->unref();
    pcLineCoords->unref();
    pcMarkerCoords->unref();
    pcDrawStyle->unref();
    pcLines->unref();
    pcLineColor->unref();
    pcMatBind->unref();
    pcMarkerColor->unref();
}

void ViewProviderPath::attach(App::DocumentObject *pcObj)
{
    ViewProviderDocumentObject::attach(pcObj);

    // Draw trajectory lines
    SoSeparator* linesep = new SoSeparator;
    linesep->addChild(pcLineColor);
    linesep->addChild(pcMatBind);
    linesep->addChild(pcDrawStyle);
    linesep->addChild(pcLineCoords);
    linesep->addChild(pcLines);

    // Draw markers
    SoSeparator* markersep = new SoSeparator;
    SoMarkerSet* marker = new SoMarkerSet;
    marker->markerIndex=SoMarkerSet::PLUS_7_7;
    markersep->addChild(pcMarkerColor);
    markersep->addChild(pcMarkerCoords);
    markersep->addChild(marker);

    pcPathRoot->addChild(pcTransform);
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
        if (colorindex.size() > 0) {
            const App::Color& c = NormalColor.getValue();            
            ParameterGrp::handle hGrp = App::GetApplication().GetParameterGroupByPath("User parameter:BaseApp/Preferences/Mod/Path");
            unsigned long rcol = hGrp->GetUnsigned("DefaultRapidPathColor",2852126975UL); // dark red (170,0,0)
            float rr,rg,rb;
            rr = ((rcol >> 24) & 0xff) / 255.0; rg = ((rcol >> 16) & 0xff) / 255.0; rb = ((rcol >> 8) & 0xff) / 255.0;
            
            pcMatBind->value = SoMaterialBinding::PER_PART;
            // resizing and writing the color vector:
            pcLineColor->diffuseColor.setNum(colorindex.size());
            SbColor* colors = pcLineColor->diffuseColor.startEditing();
            for(unsigned int i=0;i<colorindex.size();i++) {
                if (colorindex[i] == 0)
                    colors[i] = SbColor(rr,rg,rb);
                else
                    colors[i] = SbColor(c.r,c.g,c.b);
            }
            pcLineColor->diffuseColor.finishEditing();
        }
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

    if ( prop == &pcPathObj->Path) {
        
        const Toolpath &tp = pcPathObj->Path.getValue();
        if(tp.getSize()==0)
            return;
            
        ParameterGrp::handle hGrp = App::GetApplication().GetParameterGroupByPath("User parameter:BaseApp/Preferences/Mod/Part");
        float deviation = hGrp->GetFloat("MeshDeviation",0.2);
        std::vector<Base::Vector3d> points;
        std::vector<Base::Vector3d> markers;
        Base::Vector3d last(0,0,0);
        points.push_back(last);
        markers.push_back(last);
        colorindex.clear();
        bool absolute = true;
        
        for (int  i = 0; i < tp.getSize(); i++) {
            Path::Command cmd = tp.getCommand(i);
            std::string name = cmd.Name;
            Base::Vector3d next = cmd.getPlacement().getPosition();
            if (!cmd.has("x"))
                next.x = last.x;
            if (!cmd.has("y"))
                next.y = last.y;
            if (!cmd.has("z"))
                next.z = last.z;
            if (!absolute)
                next = last + next;
            
            if ( (name == "G0") || (name == "G00") || (name == "G1") || (name == "G01") ) {
                // straight line
                points.push_back(next);
                markers.push_back(next);
                last = next;
                if ( (name == "G0") || (name == "G00") )
                    colorindex.push_back(0); // rapid color
                else
                    colorindex.push_back(1); // std color
                
            } else if ( (name == "G2") || (name == "G02") || (name == "G3") || (name == "G03") ) {
                // arc
                Base::Vector3d norm;
                if ( (name == "G2") || (name == "G02") )
                    norm.Set(0,0,-1);
                else
                    norm.Set(0,0,1);
                Base::Vector3d center = (last + cmd.getCenter());
                double radius = (last - center).Length();
                double angle = (next - center).GetAngle(last - center);
                int segments = 3/(deviation/angle); //we use a rather simple rule here, provisorily
                for (int j = 1; j < segments; j++) {
                    //std::cout << "vector " << j << std::endl;
                    Base::Vector3d inter;
                    Base::Rotation rot(norm,(angle/segments)*j);
                    //std::cout << "angle " << (angle/segments)*j << std::endl;
                    rot.multVec((last - center),inter);
                    //std::cout << "result " << inter.x << " , " << inter.y << " , " << inter.z << std::endl;
                    points.push_back( center + inter);
                    colorindex.push_back(1);
                }
                //std::cout << "next " << next.x << " , " << next.y << " , " << next.z << std::endl;
                points.push_back(next);
                markers.push_back(next);
                markers.push_back(center); // add a marker at center too, why not?
                last = next;
                colorindex.push_back(1);
                
            } else if (name == "G90") {
                absolute = true;
                
            } else if (name == "G91") {
                absolute = false;
            }
        }
        
        pcLineCoords->point.deleteValues(0);
        pcLineCoords->point.setNum(points.size());
        std::vector<int> ei;
        for(unsigned int i=0;i<points.size();i++) {
            pcLineCoords->point.set1Value(i,points[i].x,points[i].y,points[i].z);
            ei.push_back(i);
        }
        int* segs = &ei[0];
        pcLines->coordIndex.setValues(0,points.size(),(const int32_t*)segs);

        pcMarkerCoords->point.deleteValues(0);
        
        // putting one market at each node makes the display awfully slow
        // leaving just one at the origin for now:
        pcMarkerCoords->point.setNum(1);
        pcMarkerCoords->point.set1Value(0,markers[0].x,markers[0].y,markers[0].z);
        //pcMarkerCoords->point.setNum(markers.size());
        //for(unsigned int i=0;i<markers.size();i++)
        //    pcMarkerCoords->point.set1Value(i,markers[i].x,markers[i].y,markers[i].z);
        
        NormalColor.touch();
        
    } else if ( prop == &pcPathObj->Placement) {
        Base::Placement pl = *(&pcPathObj->Placement.getValue());
        Base::Vector3d pos = pl.getPosition();
        double q1, q2, q3, q4;
        pl.getRotation().getValue(q1,q2,q3,q4);
        pcTransform->translation.setValue(pos.x,pos.y,pos.z);
        pcTransform->rotation.setValue(q1,q2,q3,q4);
    }
}

QIcon ViewProviderPath::getIcon() const
{
    return Gui::BitmapFactory().pixmap("Path-Toolpath");
}

