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

#include <QDir>
#include <QFileInfo>

#include <Base/Console.h>
#include <Base/VectorPy.h>
#include <Base/FileInfo.h>

#include <App/Application.h>
#include <App/Document.h>
#include <App/DocumentObjectPy.h>

#include <Gui/Command.h>

#include "ViewProviderPath.h"
#include "DlgProcessorChooser.h"
#include "ui_DlgProcessorChooser.h"

using namespace PathGui;

static PyObject * open(PyObject *self, PyObject *args)
{
    char* Name;
    if (!PyArg_ParseTuple(args, "et","utf-8",&Name))
        return NULL;
    std::string EncodedName = std::string(Name);
    PyMem_Free(Name);
    Base::FileInfo fi(EncodedName);
    if (!fi.exists())
        Py_Error(Base::BaseExceptionFreeCADError, "File not found");

    PY_TRY {
        std::string path = App::GetApplication().getHomePath();
        path += "Mod/Path/PathScripts/";
        QDir dir(QString::fromUtf8(path.c_str()), QString::fromAscii("pre_*.py"));
        QFileInfoList list = dir.entryInfoList();
        std::vector<std::string> scripts;
        for (int i = 0; i < list.size(); ++i) {
            QFileInfo fileInfo = list.at(i);
            scripts.push_back(fileInfo.baseName().toStdString());
        }
        std::string selected;
        PathGui::DlgProcessorChooser Dlg(scripts);
        if (Dlg.exec() != QDialog::Accepted) {
            Py_Return;
        }
        selected = Dlg.getSelected();
        App::Document *pcDoc = App::GetApplication().newDocument("Unnamed");
        std::ostringstream cmd;
        cmd << "Path.read(\"" << EncodedName << "\",\"" << pcDoc->getName() << "\"";
        if (!selected.empty())
            cmd << ",\"" << selected << "\"";
        cmd << ")";
        Gui::Command::runCommand(Gui::Command::Gui,"import Path");
        Gui::Command::runCommand(Gui::Command::Gui,cmd.str().c_str());
    } PY_CATCH;
    Py_Return;
}

static PyObject * importer(PyObject *self, PyObject *args)
{
    char* Name;
    char* DocName=0;
    if (!PyArg_ParseTuple(args, "et|s","utf-8",&Name,&DocName))
        return NULL;
    std::string EncodedName = std::string(Name);
    PyMem_Free(Name);
    Base::FileInfo fi(EncodedName);
    if (!fi.exists())
        Py_Error(Base::BaseExceptionFreeCADError, "File not found");

    PY_TRY {
        std::string path = App::GetApplication().getHomePath();
        path += "Mod/Path/PathScripts/";
        QDir dir(QString::fromUtf8(path.c_str()), QString::fromAscii("pre_*.py"));
        QFileInfoList list = dir.entryInfoList();
        std::vector<std::string> scripts;
        for (int i = 0; i < list.size(); ++i) {
            QFileInfo fileInfo = list.at(i);
            scripts.push_back(fileInfo.baseName().toStdString());
        }
        std::string selected;
        PathGui::DlgProcessorChooser Dlg(scripts);
        if (Dlg.exec() != QDialog::Accepted) {
            Py_Return;
        }
        selected = Dlg.getSelected();

        App::Document *pcDoc = 0;
        if (DocName)
            pcDoc = App::GetApplication().getDocument(DocName);
        else
            pcDoc = App::GetApplication().getActiveDocument();

        if (!pcDoc) {
            pcDoc = App::GetApplication().newDocument(DocName);
        }

        std::ostringstream cmd;
        cmd << "Path.read(\"" << EncodedName << "\",\"" << pcDoc->getName() << "\"";
        if (!selected.empty())
            cmd << ",\"" << selected << "\"";
        cmd << ")";
        Gui::Command::runCommand(Gui::Command::Gui,"import Path");
        Gui::Command::runCommand(Gui::Command::Gui,cmd.str().c_str());
    } PY_CATCH;
    Py_Return;
}

static PyObject * exporter(PyObject *self, PyObject *args)
{
    PyObject* object;
    char* Name;
    if (!PyArg_ParseTuple(args, "Oet",&object,"utf-8",&Name))
        return NULL;
    std::string EncodedName = std::string(Name);
    PyMem_Free(Name);

    PY_TRY {
        Py::Sequence list(object);
        if (list.size() == 0) {
            Py_Return;
        } else if (list.size() > 1)
            Py_Error(Base::BaseExceptionFreeCADError, "Unable to export more than one object to a GCode file");
        PyObject* item = list[0].ptr();
        if (PyObject_TypeCheck(item, &(App::DocumentObjectPy::Type))) {
            App::DocumentObject* obj = static_cast<App::DocumentObjectPy*>(item)->getDocumentObjectPtr();
            std::string path = App::GetApplication().getHomePath();
            path += "Mod/Path/PathScripts/";
            QDir dir(QString::fromUtf8(path.c_str()), QString::fromAscii("post_*.py"));
            QFileInfoList list = dir.entryInfoList();
            std::vector<std::string> scripts;
            for (int i = 0; i < list.size(); ++i) {
                QFileInfo fileInfo = list.at(i);
                scripts.push_back(fileInfo.baseName().toStdString());
            }
            std::string selected;
            PathGui::DlgProcessorChooser Dlg(scripts);
            if (Dlg.exec() != QDialog::Accepted) {
                Py_Return;
            }
            selected = Dlg.getSelected();
            std::ostringstream cmd;
            App::Document* doc = obj->getDocument();
            cmd << "Path.write(FreeCAD.getDocument(\"" << doc->getName() << "\").getObject(\"" << obj->getNameInDocument() << "\"),\"" << EncodedName << "\"";
            if (!selected.empty())
                cmd << ",\"" << selected << "\"";
            cmd << ")";
            Gui::Command::runCommand(Gui::Command::Gui,"import Path");
            Gui::Command::runCommand(Gui::Command::Gui,cmd.str().c_str());
        }
    } PY_CATCH;
    Py_Return;
}

/* registration table  */
struct PyMethodDef PathGui_methods[] = {
    {"open"        ,open       ,METH_VARARGS,
     "open(filename): Opens a GCode file as a new document"},
    {"insert"      ,importer   ,METH_VARARGS,
     "insert(filename,docname): Imports a given GCode file into the given document"},
    {"export"      ,exporter   ,METH_VARARGS,
     "export(objectslist,filename): Exports a given list of Path objects to a GCode file"},
    {NULL, NULL}        /* end of table marker */
};
