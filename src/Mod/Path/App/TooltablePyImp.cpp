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

#include "Mod/Path/App/Tooltable.h"

// inclusion of the generated files (generated out of ToolPy.xml and TooltablePy.xml)
#include "ToolPy.h"
#include "ToolPy.cpp"
#include "TooltablePy.h"
#include "TooltablePy.cpp"

using namespace Path;



// ToolPy



// returns a string which represents the object e.g. when printed in python
std::string ToolPy::representation(void) const
{
    std::stringstream str;
    str.precision(5);
    str << "Tool ";
    str << getToolPtr()->Name;
    return str.str();
}

PyObject *ToolPy::PyMake(struct _typeobject *, PyObject *, PyObject *)  // Python wrapper
{
    // create a new instance of ToolPy and the Twin object 
    return new ToolPy(new Tool);
}

// constructor method
int ToolPy::PyInit(PyObject* args, PyObject* kwd)
{
    PyObject *pos;
    char *name="Default tool";
    char *type = "Undefined";
    char *mat = "Undefined";
    PyObject *dia = 0;
    PyObject *len = 0;
    PyObject *fla = 0;
    PyObject *cor = 0;
    PyObject *ang = 0;
    PyObject *hei = 0;

    static char *kwlist[] = {"name", "tooltype", "material", "diameter", "lengthOffset", "flatRadius", "cornerRadius", "cuttingEdgeAngle", "cuttingEdgeHeight" ,NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwd, "|sssOOOOOO", kwlist,
                                     &name, &type, &mat, &dia, &len, &fla, &cor, &ang, &hei ))
        return -1;

    getToolPtr()->Name = name;
    std::string typeStr(type);
    if(typeStr=="Drill")
        getToolPtr()->Type = Tool::DRILL;
    else if(typeStr=="CenterDrill")
        getToolPtr()->Type = Tool::CENTERDRILL;

    if(typeStr=="Countersink")
        getToolPtr()->Type = Tool::COUNTERSINK;

    if(typeStr=="Reamer")
        getToolPtr()->Type = Tool::REAMER;

    if(typeStr=="Tap")
        getToolPtr()->Type = Tool::TAP;


    else if(typeStr=="EndMill")
        getToolPtr()->Type = Tool::ENDMILL;
    else if(typeStr=="SlotCutter")
        getToolPtr()->Type = Tool::SLOTCUTTER;
    else if(typeStr=="BallEndMill")
        getToolPtr()->Type = Tool::BALLENDMILL;
    else if(typeStr=="ChamferMill")
        getToolPtr()->Type = Tool::CHAMFERMILL;
    else if(typeStr=="Engraver")
        getToolPtr()->Type = Tool::ENGRAVER;
    else 
        getToolPtr()->Type = Tool::UNDEFINED;
    std::string matStr(mat);
    if(matStr=="Steel")
        getToolPtr()->Material = Tool::STEEL;
    else if(matStr=="Carbide")
        getToolPtr()->Material = Tool::CARBIDE;
    else 
        getToolPtr()->Material = Tool::MATUNDEFINED;

    getToolPtr()->Diameter = PyFloat_AsDouble(dia);
    getToolPtr()->LengthOffset = PyFloat_AsDouble(len);
    getToolPtr()->FlatRadius = PyFloat_AsDouble(fla);
    getToolPtr()->CornerRadius = PyFloat_AsDouble(cor);
    getToolPtr()->CuttingEdgeAngle = PyFloat_AsDouble(ang);
    getToolPtr()->CuttingEdgeHeight = PyFloat_AsDouble(hei);

    return 0;
}

// attributes get/setters

Py::String ToolPy::getName(void) const
{
    return Py::String(getToolPtr()->Name.c_str());
}

void ToolPy::setName(Py::String arg)
{
    std::string name = arg.as_std_string();
    getToolPtr()->Name = name;
}

Py::String ToolPy::getToolType(void) const
{
    if(getToolPtr()->Type == Tool::DRILL)
        return Py::String("Drill");
    else if(getToolPtr()->Type == Tool::CENTERDRILL)
        return Py::String("CenterDrill");

    else if(getToolPtr()->Type == Tool::REAMER)
        return Py::String("Reamer");

    else if(getToolPtr()->Type == Tool::TAP)
        return Py::String("Tap");

    else if(getToolPtr()->Type == Tool::ENDMILL)
        return Py::String("EndMill");
    else if(getToolPtr()->Type == Tool::SLOTCUTTER)
        return Py::String("SlotCutter");
    else if(getToolPtr()->Type == Tool::BALLENDMILL)
        return Py::String("BallEndMill");
    else if(getToolPtr()->Type == Tool::CHAMFERMILL)
        return Py::String("ChamferMill");
    else if(getToolPtr()->Type == Tool::ENGRAVER)
        return Py::String("Engraver");
    else
        return Py::String("Undefined");
}

void ToolPy::setToolType(Py::String arg)
{
    std::string typeStr(arg.as_std_string());
    if(typeStr=="Drill")
        getToolPtr()->Type = Tool::DRILL;
    else if(typeStr=="CenterDrill")
        getToolPtr()->Type = Tool::CENTERDRILL;

    else if(typeStr=="Reamer")
        getToolPtr()->Type = Tool::REAMER;

    else if(typeStr=="Tap")
        getToolPtr()->Type = Tool::TAP;


    else if(typeStr=="EndMill")
        getToolPtr()->Type = Tool::ENDMILL;
    else if(typeStr=="SlotCutter")
        getToolPtr()->Type = Tool::SLOTCUTTER;
    else if(typeStr=="BallEndMill")
        getToolPtr()->Type = Tool::BALLENDMILL;
    else if(typeStr=="ChamferMill")
        getToolPtr()->Type = Tool::CHAMFERMILL;
    else if(typeStr=="Engraver")
        getToolPtr()->Type = Tool::ENGRAVER;
    else 
        getToolPtr()->Type = Tool::UNDEFINED;
}

Py::String ToolPy::getMaterial(void) const
{
    if(getToolPtr()->Material == Tool::STEEL)
        return Py::String("Steel");
    else if(getToolPtr()->Material == Tool::CARBIDE)
        return Py::String("Carbide");
    else
        return Py::String("Undefined");
}

void ToolPy::setMaterial(Py::String arg)
{
    std::string matStr(arg.as_std_string());
    if(matStr=="Steel")
        getToolPtr()->Material = Tool::STEEL;
    else if(matStr=="Carbide")
        getToolPtr()->Material = Tool::CARBIDE;
    else 
        getToolPtr()->Material = Tool::MATUNDEFINED;
}

Py::Float ToolPy::getDiameter(void) const
{
    return Py::Float(getToolPtr()->Diameter);
}

void  ToolPy::setDiameter(Py::Float arg)
{
    getToolPtr()->Diameter = arg.operator double();
}

Py::Float ToolPy::getLengthOffset(void) const
{
    return Py::Float(getToolPtr()->LengthOffset);
}

void  ToolPy::setLengthOffset(Py::Float arg)
{
    getToolPtr()->LengthOffset = arg.operator double();
}

Py::Float ToolPy::getFlatRadius(void) const
{
    return Py::Float(getToolPtr()->FlatRadius);
}

void  ToolPy::setFlatRadius(Py::Float arg)
{
    getToolPtr()->FlatRadius = arg.operator double();
}

Py::Float ToolPy::getCornerRadius(void) const
{
    return Py::Float(getToolPtr()->CornerRadius);
}

void  ToolPy::setCornerRadius(Py::Float arg)
{
    getToolPtr()->CornerRadius = arg.operator double();
}

Py::Float ToolPy::getCuttingEdgeAngle(void) const
{
    return Py::Float(getToolPtr()->CuttingEdgeAngle);
}

void  ToolPy::setCuttingEdgeAngle(Py::Float arg)
{
    getToolPtr()->CuttingEdgeAngle = arg.operator double();
}

Py::Float ToolPy::getCuttingEdgeHeight(void) const
{
    return Py::Float(getToolPtr()->CuttingEdgeHeight);
}

void  ToolPy::setCuttingEdgeHeight(Py::Float arg)
{
    getToolPtr()->CuttingEdgeHeight = arg.operator double();
}

// custom attributes get/set

PyObject *ToolPy::getCustomAttributes(const char* /*attr*/) const
{
    return 0;
}

int ToolPy::setCustomAttributes(const char* /*attr*/, PyObject* /*obj*/)
{
    return 0; 
}




// TooltablePy




// returns a string which represents the object e.g. when printed in python
std::string TooltablePy::representation(void) const
{
    std::stringstream str;
    str.precision(5);
    str << "Tooltable containing ";
    str << getTooltablePtr()->getSize() << " tools";
    return str.str();
}

PyObject *TooltablePy::PyMake(struct _typeobject *, PyObject *, PyObject *)  // Python wrapper
{
    return new TooltablePy(new Tooltable);
}

// constructor method
int TooltablePy::PyInit(PyObject* args, PyObject* /*kwd*/)
{
    PyObject *pcObj=0;
    if (!PyArg_ParseTuple(args, "|O!", &(PyList_Type), &pcObj))
        return -1;

    if (pcObj) {
        Py::List list(pcObj);
        for (Py::List::iterator it = list.begin(); it != list.end(); ++it) {
            if (PyObject_TypeCheck((*it).ptr(), &(Path::ToolPy::Type))) {
                Path::Tool &tool = *static_cast<Path::ToolPy*>((*it).ptr())->getToolPtr();
                getTooltablePtr()->addTool(tool);
            }
        }
    }
    return 0;
}


// Commands get/set

Py::List TooltablePy::getTools(void) const
{
    Py::List list;
    for(unsigned int i = 0; i < getTooltablePtr()->getSize(); i++)
        list.append(Py::Object(new Path::ToolPy(new Path::Tool(getTooltablePtr()->getTool(i)))));
    return list;
}

void TooltablePy::setTools(Py::List list)
{
    getTooltablePtr()->Tools.clear();
    for (Py::List::iterator it = list.begin(); it != list.end(); ++it) {
        if (PyObject_TypeCheck((*it).ptr(), &(Path::ToolPy::Type))) {
            Path::Tool &tool = *static_cast<Path::ToolPy*>((*it).ptr())->getToolPtr();
            getTooltablePtr()->addTool(tool);
        } else {
            throw Py::Exception("The list can only contain Path Tools");
        }
    }
}

// specific methods

PyObject* TooltablePy::addTools(PyObject * args)
{
    PyObject* o;
    if (PyArg_ParseTuple(args, "O!", &(Path::ToolPy::Type), &o)) {
        Path::Tool &tool = *static_cast<Path::ToolPy*>(o)->getToolPtr();
        getTooltablePtr()->addTool(tool);
        return new TooltablePy(new Path::Tooltable(*getTooltablePtr()));
        //Py_Return;
    }
    PyErr_Clear();
    if (PyArg_ParseTuple(args, "O!", &(PyList_Type), &o)) {
        Py::List list(o);
        for (Py::List::iterator it = list.begin(); it != list.end(); ++it) {
            if (PyObject_TypeCheck((*it).ptr(), &(Path::ToolPy::Type))) {
                Path::Tool &tool = *static_cast<Path::ToolPy*>((*it).ptr())->getToolPtr();
                getTooltablePtr()->addTool(tool);
            }
        }
        return new TooltablePy(new Path::Tooltable(*getTooltablePtr()));
    }
    Py_Error(Base::BaseExceptionFreeCADError, "Wrong parameters - tool or list of tools expected");
}

PyObject* TooltablePy::insertTool(PyObject * args)
{
    PyObject* o;
    int pos = -1;
    if (PyArg_ParseTuple(args, "O!|i", &(Path::ToolPy::Type), &o, &pos)) {
        Path::Tool &tool = *static_cast<Path::ToolPy*>(o)->getToolPtr();
        getTooltablePtr()->insertTool(tool,pos);
        return new TooltablePy(new Path::Tooltable(*getTooltablePtr()));
    }
    Py_Error(Base::BaseExceptionFreeCADError, "Wrong parameters - expected tool and optional integer");
}

PyObject* TooltablePy::deleteTool(PyObject * args)
{
    int pos = -1;
    if (PyArg_ParseTuple(args, "|i", &pos)) {
        getTooltablePtr()->deleteTool(pos);
        return new TooltablePy(new Path::Tooltable(*getTooltablePtr()));
    }
    Py_Error(Base::BaseExceptionFreeCADError, "Wrong parameters - expected an integer (optional)");
}

// custom attributes get/set

PyObject *TooltablePy::getCustomAttributes(const char* /*attr*/) const
{
    return 0;
}

int TooltablePy::setCustomAttributes(const char* /*attr*/, PyObject* /*obj*/)
{
    return 0; 
}


