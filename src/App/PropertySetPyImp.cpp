/***************************************************************************
 *   Copyright (c) Yorik van Havre <yorik@uncreated.net> 2017              *
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
# include <sstream>
#endif

#include "PropertyContainer.h"
#include "Property.h"
#include "Application.h"

// inclution of the generated files (generated out of PropertySetPy.xml)
#include "PropertySetPy.h"
#include "PropertySetPy.cpp"

using namespace App;

// returns a string which represent the object e.g. when printed in python
std::string PropertySetPy::representation(void) const
{
    return std::string("<property set>");
}

PyObject*  PropertySetPy::getProperty(PyObject *args)
{
    char *pstr;
    if (!PyArg_ParseTuple(args, "s", &pstr))     // convert args: Python->C
        return NULL;                             // NULL triggers exception
    App::Property* prop = getPropertySetPtr()->getProperty(pstr);
    if (prop) {
        return prop->getPyObject();
    }
    else {
        PyErr_Format(PyExc_AttributeError, "Property set has no property '%s'", pstr);
        return NULL;
    }
}

PyObject*  PropertySetPy::getPropertyType(PyObject *args)
{
    char *pstr;
    if (!PyArg_ParseTuple(args, "s", &pstr))     // convert args: Python->C
        return NULL;                             // NULL triggers exception
    Property* prop = getPropertySetPtr()->getProperty(pstr);
    if (!prop) {
        PyErr_Format(PyExc_AttributeError, "Property set has no property '%s'", pstr);
        return 0;
    }
    Py::String str(getPropertySetPtr()->getPropertyType(pstr));
    return Py::new_reference_to(str);
}

PyObject*  PropertySetPy::getPropertyDocumentation(PyObject *args)
{
    char *pstr;
    if (!PyArg_ParseTuple(args, "s", &pstr))     // convert args: Python->C
        return NULL;                             // NULL triggers exception
    Property* prop = getPropertySetPtr()->getProperty(pstr);
    if (!prop) {
        PyErr_Format(PyExc_AttributeError, "Property set has no property '%s'", pstr);
        return 0;
    }
    const char* docu = getPropertySetPtr()->getPropertyDocumentation(pstr);
    if (docu)
        return Py::new_reference_to(Py::String(docu));
    else
        return Py::new_reference_to(Py::String(""));
}

PyObject*  PropertySetPy::addProperty(PyObject *args)
{
    char *tstr; // type
    char *nstr; // name
    char *dstr; // doc (optional)
    if (!PyArg_ParseTuple(args, "ss|s", &tstr, &nstr, &dstr))     // convert args: Python->C
        return NULL;                             // NULL triggers exception
    getPropertySetPtr()->addProperty(tstr,nstr,dstr);
    return 0;
}

PyObject*  PropertySetPy::removeProperty(PyObject *args)
{
    char *pstr;
    if (!PyArg_ParseTuple(args, "s", &pstr))     // convert args: Python->C
        return NULL;                             // NULL triggers exception
    Property* prop = getPropertySetPtr()->getProperty(pstr);
    if (!prop) {
        PyErr_Format(PyExc_AttributeError, "Property set has no property '%s'", pstr);
        return 0;
    }
    bool ret = getPropertySetPtr()->removeProperty(pstr);
    return Py_BuildValue("O", (ret ? Py_True : Py_False));
}

Py::List PropertySetPy::getPropertiesList(void) const
{
    Py::List ret;
    std::vector<std::string> names = getPropertySetPtr()->getPropertiesNames();
    for (std::vector<std::string>::const_iterator it=names.begin(); it!=names.end(); ++it)
        ret.append(Py::String(*it));
    return ret;
}

PyObject *PropertySetPy::getCustomAttributes(const char* attr) const
{
    return 0;
}

int PropertySetPy::setCustomAttributes(const char* attr, PyObject *obj)
{
    return 0;
}
