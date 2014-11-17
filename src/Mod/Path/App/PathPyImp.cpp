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

#include "Mod/Path/App/Path.h"

// inclusion of the generated files (generated out of PathPy.xml)
#include "PathPy.h"
#include "PathPy.cpp"

#include "CommandPy.h"

using namespace Path;

// returns a string which represents the object e.g. when printed in python
std::string PathPy::representation(void) const
{
    std::stringstream str;
    str.precision(5);
    str << "Path [ ";
    str << "size:" << getToolpathPtr()->getSize() << " ";
    str << "length:" << getToolpathPtr()->getLength();
    str << " ]";

    return str.str();
}

PyObject *PathPy::PyMake(struct _typeobject *, PyObject *, PyObject *)  // Python wrapper
{
    // create a new instance of PathPy and the Twin object 
    return new PathPy(new Toolpath);
}

// constructor method
int PathPy::PyInit(PyObject* args, PyObject* /*kwd*/)
{
    PyObject *pcObj=0;
    if (!PyArg_ParseTuple(args, "|O!", &(PyList_Type), &pcObj))
        return -1;

    if (pcObj) {
        Py::List list(pcObj);
        for (Py::List::iterator it = list.begin(); it != list.end(); ++it) {
            if (PyObject_TypeCheck((*it).ptr(), &(Path::CommandPy::Type))) {
                Path::Command &cmd = *static_cast<Path::CommandPy*>((*it).ptr())->getCommandPtr();
                getToolpathPtr()->addCommand(cmd);
            }
        }
    }
    return 0;
}


PyObject* PathPy::addCommands(PyObject * args)
{
    PyObject* o;
    if (PyArg_ParseTuple(args, "O!", &(Path::CommandPy::Type), &o)) {
        Path::Command &cmd = *static_cast<Path::CommandPy*>(o)->getCommandPtr();
        getToolpathPtr()->addCommand(cmd);
        return new PathPy(new Path::Toolpath(*getToolpathPtr()));
        //Py_Return;
    }
    PyErr_Clear();
    if (PyArg_ParseTuple(args, "O!", &(PyList_Type), &o)) {
        Py::List list(o);
        for (Py::List::iterator it = list.begin(); it != list.end(); ++it) {
            if (PyObject_TypeCheck((*it).ptr(), &(Path::CommandPy::Type))) {
                Path::Command &cmd = *static_cast<Path::CommandPy*>((*it).ptr())->getCommandPtr();
                getToolpathPtr()->addCommand(cmd);
            }
        }
        return new PathPy(new Path::Toolpath(*getToolpathPtr()));
    }
    Py_Error(Base::BaseExceptionFreeCADError, "Wrong parameters - command or list of commands expected");
}

Py::List PathPy::getCommands(void) const
{
    Py::List list;
    for(unsigned int i = 0; i < getToolpathPtr()->getSize(); i++)
        list.append(Py::Object(new Path::CommandPy(new Path::Command(getToolpathPtr()->getCommand(i)))));
    return list;
}

Py::Float PathPy::getLength(void) const
{
    return Py::Float(getToolpathPtr()->getLength());
}

void PathPy::setCommands(Py::List)
{
    // TODO
}

PyObject *PathPy::getCustomAttributes(const char* /*attr*/) const
{
    return 0;
}

int PathPy::setCustomAttributes(const char* /*attr*/, PyObject* /*obj*/)
{
    return 0; 
}


