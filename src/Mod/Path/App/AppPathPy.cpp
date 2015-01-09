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
# include <Python.h>
#endif

#include <Base/Console.h>
#include <Base/VectorPy.h>
#include <Base/FileInfo.h>
#include <Base/Interpreter.h>
#include <App/Document.h>
#include <App/DocumentObjectPy.h>
#include <App/Application.h>

#include "CommandPy.h"
#include "PathPy.h"
#include "Path.h"
#include "FeaturePath.h"
#include "FeaturePathCompound.h"

using namespace Path;


static PyObject * write (PyObject *self, PyObject *args)
{
    char* Name;
    PyObject* pObj;
    char* Pre = "";
    if (!PyArg_ParseTuple(args, "Oet|s",&pObj,"utf-8",&Name,&Pre))
        return NULL;
    std::string EncodedName = std::string(Name);
    PyMem_Free(Name);

    Base::FileInfo file(EncodedName.c_str());
    
    if (PyObject_TypeCheck(pObj, &(App::DocumentObjectPy::Type))) {
        App::DocumentObject* obj = static_cast<App::DocumentObjectPy*>(pObj)->getDocumentObjectPtr();
        if (obj->getTypeId().isDerivedFrom(Base::Type::fromName("Path::Feature"))) {
            const Toolpath& path = static_cast<Path::Feature*>(obj)->Path.getValue();
            std::string gcode = path.toGCode();

            if (strcmp(Pre, "") != 0) {
                // use a python Postprocessor
                // by calling its parse() function
                std::string modpath = "PathScripts.";
                modpath += Pre;
                PyObject *pModule, *pFunc, *pName, *pInput, *pOutput, *pArgs;
                // get the global interpreter lock otherwise the app may crash with the error
                // 'PyThreadState_Get: no current thread' (see pystate.c)
                Base::PyGILStateLocker lock;
                pName = PyString_FromString(modpath.c_str());
                pModule = PyImport_Import(pName);
                if (pModule == NULL) {
                    // try to import the file from the user folder
                    pName = PyString_FromString(Pre);
                    pModule = PyImport_Import(pName);
                }
                if (pModule != NULL) {
                    pFunc = PyObject_GetAttrString(pModule,"parse");
                    if (pFunc && PyCallable_Check(pFunc)) {
                        // function arguments must be packed into a tuple
                        pInput = PyString_FromString(gcode.c_str());
                        pArgs = PyTuple_New(1);
                        PyTuple_SetItem(pArgs, 0, pInput);
                        pOutput = PyObject_CallObject(pFunc, pArgs);
                        if (pOutput != NULL) {
                            gcode = std::string(PyString_AsString(pOutput));
                        } else
                            Py_Error(Base::BaseExceptionFreeCADError, "Postprocessor failed to parse the given file");
                    } else
                        Py_Error(Base::BaseExceptionFreeCADError, "Postprocessor does not contain a valid parse() function");
                } else
                    Py_Error(Base::BaseExceptionFreeCADError, "Unable to load the given postprocessor");
                Py_DECREF(pName);
                Py_DECREF(pInput);
                Py_DECREF(pOutput);
                Py_DECREF(pModule);
                Py_DECREF(pFunc);
            }
    
            std::ofstream ofile(EncodedName.c_str());
            ofile << gcode;
            ofile.close();
        } else
            Py_Error(Base::BaseExceptionFreeCADError, "The given file is not a path");
    }
    Py_Return;
}


static PyObject * read (PyObject *self, PyObject *args)
{
    char* Name;
    const char* DocName;
    char* Pre = "";
    if (!PyArg_ParseTuple(args, "ets|s","utf-8",&Name,&DocName,&Pre))
        return NULL;
    std::string EncodedName = std::string(Name);
    PyMem_Free(Name);

    Base::FileInfo file(EncodedName.c_str());
    if (!file.exists())
        Py_Error(Base::BaseExceptionFreeCADError, "File doesn't exist");
    App::Document *pcDoc = App::GetApplication().getDocument(DocName);
    if (!pcDoc)
        pcDoc = App::GetApplication().newDocument(DocName);

    // read the gcode file
    std::ifstream filestr(file.filePath().c_str());
    std::stringstream buffer;
    buffer << filestr.rdbuf();
    std::string gcode = buffer.str();
    std::vector<std::string> gcodelist;
    bool isList = false;
    if (strcmp(Pre, "") != 0) {
        // use a python Preprocessor
        // by calling its parse() function
        std::string modpath = "PathScripts.";
        modpath += Pre;
        PyObject *pModule, *pFunc, *pName, *pInput, *pOutput, *pArgs;
        // get the global interpreter lock otherwise the app may crash with the error
        // 'PyThreadState_Get: no current thread' (see pystate.c)
        Base::PyGILStateLocker lock;
        pName = PyString_FromString(modpath.c_str());
        pModule = PyImport_Import(pName);
        if (pModule == NULL) {
            // try to import the file from the user folder
            pName = PyString_FromString(Pre);
            pModule = PyImport_Import(pName);
        }
        if (pModule != NULL) {
            pFunc = PyObject_GetAttrString(pModule,"parse");
            if (pFunc && PyCallable_Check(pFunc)) {
                // function arguments must be packed into a tuple
                pInput = PyString_FromString(gcode.c_str());
                pArgs = PyTuple_New(1);
                PyTuple_SetItem(pArgs, 0, pInput);
                pOutput = PyObject_CallObject(pFunc, pArgs);
                if (pOutput != NULL) {
                    if (PyObject_TypeCheck(pOutput,&(PyString_Type))) {
                        gcode = std::string(PyString_AsString(pOutput));
                    } else if (PyObject_TypeCheck(pOutput,&(PyList_Type))) {
                        isList = true;
                        Py::List list(pOutput);
                        for (Py::List::iterator it = list.begin(); it != list.end(); ++it) {
                            if (PyObject_TypeCheck((*it).ptr(), &(PyString_Type))) {
                                gcodelist.push_back(std::string(PyString_AsString((*it).ptr())));
                            } else
                                Py_Error(Base::BaseExceptionFreeCADError, "Preprocessor must return a string or a list of strings");
                        }
                    } else
                        Py_Error(Base::BaseExceptionFreeCADError, "Preprocessor must return a string or a list of strings");
                } else
                    Py_Error(Base::BaseExceptionFreeCADError, "Preprocessor failed to parse the given file");
            } else
                Py_Error(Base::BaseExceptionFreeCADError, "Preprocessor does not contain a valid parse() function");
        } else
            Py_Error(Base::BaseExceptionFreeCADError, "Unable to load the given preprocessor");
        Py_DECREF(pName);
        Py_DECREF(pInput);
        Py_DECREF(pOutput);
        Py_DECREF(pModule);
        Py_DECREF(pFunc);
    }
    
    if (isList) {
        std::vector<App::DocumentObject*> children;
        for(std::vector<std::string>::iterator it = gcodelist.begin();it!=gcodelist.end();++it) {
            Toolpath path;
            path.setFromGCode((*it));
            Path::Feature *object = static_cast<Path::Feature *>(pcDoc->addObject("Path::Feature","Path"));
            object->Path.setValue(path);
            children.push_back(static_cast<App::DocumentObject*>(object));
        }
        Path::FeatureCompound *compound = static_cast<Path::FeatureCompound *>(pcDoc->addObject("Path::FeatureCompound",file.fileNamePure().c_str()));
        compound->Group.setValues(children);
    } else {
        Toolpath path;
        path.setFromGCode(gcode);
        Path::Feature *object = static_cast<Path::Feature *>(pcDoc->addObject("Path::Feature",file.fileNamePure().c_str()));
        object->Path.setValue(path);
    }
    pcDoc->recompute();
    Py_Return;
}


static PyObject * show (PyObject *self, PyObject *args)
{
    PyObject *pcObj;
    if (!PyArg_ParseTuple(args, "O!", &(PathPy::Type), &pcObj))     // convert args: Python->C
        return NULL;                             // NULL triggers exception

    PY_TRY {
        App::Document *pcDoc = App::GetApplication().getActiveDocument(); 	 
        if (!pcDoc)
            pcDoc = App::GetApplication().newDocument();
        PathPy* pPath = static_cast<PathPy*>(pcObj);
        Path::Feature *pcFeature = (Path::Feature *)pcDoc->addObject("Path::Feature", "Path");
        Path::Toolpath* pa = pPath->getToolpathPtr();
        if (!pa) {
            PyErr_SetString(PyExc_ReferenceError,
                "object doesn't reference a valid path");
            return 0;
        }
        // copy the data
        pcFeature->Path.setValue(*pa);
    } PY_CATCH;

    Py_Return;
}


/* registration table  */
struct PyMethodDef Path_methods[] = {
    {"write"      ,write     ,METH_VARARGS,
     "write(object,filename,[preprocessor]): Exports a given path object to a GCode file, optionally passing it through a post-processor"},
    {"read"       ,read      ,METH_VARARGS,
     "read(filename,document,[preprocessor]): Imports a GCode file into the given document, optionally passing it through a pre-processor"},
    {"show"       ,show      ,METH_VARARGS,
     "show(path): Add the path to the active document or create one if no document exists."},
    {NULL, NULL}        /* end of table marker */
};
