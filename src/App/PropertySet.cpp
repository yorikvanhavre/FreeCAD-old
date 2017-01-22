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
#   include <assert.h>
#endif

/// Here the FreeCAD includes sorted by Base,App,Gui......
#include <CXX/Objects.hxx>
#include <Base/Exception.h>
#include <Base/Reader.h>
#include <Base/Writer.h>
#include <Base/Console.h>
#include <Base/BaseClass.h>
#include <Base/Tools.h>

#include "DocumentObject.h"
#include "DocumentObjectPy.h"
#include "Document.h"

#include "PropertySet.h"

using namespace App;
using namespace Base;
using namespace std;


//**************************************************************************
//**************************************************************************
// PropertySet
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TYPESYSTEM_SOURCE(App::PropertySet , App::Property)


PropertySet::PropertySet()
{
}

PropertySet::~PropertySet()
{
}

int PropertySet::getSize(void) const
{
    return static_cast<int>(_mValueMap.size());
}

unsigned int PropertySet::getMemSize (void) const
{
    unsigned int size = 0;
    for (std::map<std::string,PropertySetData>::const_iterator it = _mValueMap.begin(); it != _mValueMap.end(); ++it)
        size += it->second.Prop->getMemSize();
    return size;
}

std::vector<std::string> PropertySet::getPropertiesNames() const
{
    std::vector<std::string> names;
    for (std::map<std::string,PropertySetData>::const_iterator it = _mValueMap.begin(); it != _mValueMap.end(); ++it)
        names.push_back(it->first);
    return names;
}

PropertySetData* PropertySet::getPropertyData(const char* name) const
{
    for (std::map<std::string,PropertySetData>::const_iterator it = _mValueMap.begin(); it != _mValueMap.end(); ++it) {
        if(strcmp(it->first.c_str(),name) == 0)
            return *it->second;
    }
    return 0;
}

Property* PropertySet::getProperty(const char* name) const
{
    for (std::map<std::string,PropertySetData>::const_iterator it = _mValueMap.begin(); it != _mValueMap.end(); ++it) {
        if(strcmp(it->first.c_str(),name) == 0)
            return new it->second.Prop;
    }
    return 0;
}

short PropertySet::getPropertyType(const char *name) const
{
    PropertySetData* propdata = getPropertyData(name);
    if(propdata)
        return propdata->Type;
    else
        return 0;
}

const char* PropertySet::getPropertyDocumentation(const char *name) const
{
    PropertySetData* propdata = getPropertyData(name);
    if(propdata)
        return propdata->Docu;
    else
        return 0;
}

std::string PropertySet::getUniquePropertyName(const char *Name) const
{
    std::string CleanName = Base::Tools::getIdentifier(Name);

    // name in use?
    PropertySetData* propdata = getPropertyData(CleanName);
    if(!propdata) {
        // name is not in use - free to go
        return CleanName;
    } else {
        std::vector<std::string> names = getPropertiesNames();
        return Base::Tools::getUniqueName(CleanName, names);
    }
}

std::string PropertySet::encodeAttribute(const std::string& str) const
{
    std::string tmp;
    for (std::string::const_iterator it = str.begin(); it != str.end(); ++it) {
        if (*it == '<')
            tmp += "&lt;";
        else if (*it == '"')
            tmp += "&quot;";
        else if (*it == '\'')
            tmp += "&apos;";
        else if (*it == '&')
            tmp += "&amp;";
        else if (*it == '>')
            tmp += "&gt;";
        else if (*it == '\r')
            tmp += "&#xD;";
        else if (*it == '\n')
            tmp += "&#xA;";
        else
            tmp += *it;
    }
    return tmp;
}

Property* PropertySet::addProperty(const char* type, const char* name, const char* doc)
{
    // check type
    Base::BaseClass* base = static_cast<Base::BaseClass*>(Base::Type::createInstanceByName(type,true));
    if (!base)
        return 0;
    if (!base->getTypeId().isDerivedFrom(Property::getClassTypeId())) {
        delete base;
        std::stringstream str;
        str << "'" << type << "' is not a property type";
        throw Base::Exception(str.str());
    }
    // get unique name
    Property* pcProperty = static_cast<Property*>(base);
    std::string ObjectName;
    if (name && *name != '\0')
        ObjectName = getUniquePropertyName(name);
    else
        ObjectName = getUniquePropertyName(type);
    // create property
    pcProperty->setContainer(this);
    PropertySetData data;
    data.Prop = pcProperty;
    data.Docu = (doc ? doc : "");
    data.Type = type;
    _mValueMap[ObjectName] = data;
    GetApplication().signalAppendDynamicProperty(*pcProperty);
    return pcProperty;
}

bool PropertySet::removeProperty(const char* name)
{
    std::map<std::string,PropertySetData>::iterator it = _mValueMap.find(name);
    if (it != _mValueMap.end()) {
        GetApplication().signalRemoveDynamicProperty(*it->second.Prop);
        delete it->second.Prop;
        props.erase(it);
        return true;
    }
    return false;
}

Property* PropertySet::operator[] (const char* name) const
{
    PropertySetData* propdata = getPropertyData(name);
    if(propdata)
        return propdata->Prop;
    else {
        std::stringstream str;
        str << "'Key " << name << "' not found";
        throw Base::Exception(str.str());
    }
}

void PropertySet::Save (Base::Writer &writer) const 
{  
    size_t size = _mValueMap.size();

    writer.incInd(); // indentation for 'Properties Count'
    writer.Stream() << writer.ind() << "<Properties Count=\"" << size << "\">" << endl;
    for(std::map<std::string,PropertySetData>::const_iterator it = _mValueMap.begin(); it != _mValueMap.end(); ++it) {
        writer.incInd(); // indentation for 'Property name'
        writer.Stream() << writer.ind() << "<Property name=\"" << it->first 
                        << "\" type=\"" << it->second.Type 
                        << "\" doc=\"" << encodeAttribute(it->second.Docu)
                        << "\">" << endl;
        writer.incInd(); // indentation for the actual property
        try {
            // We must make sure to handle all exceptions accordingly so that
            // the project file doesn't get invalidated. In the error case this
            // means to proceed instead of aborting the write operation.
            it->second.Prop->Save(writer);
        }
        catch (const Base::Exception &e) {
            Base::Console().Error("%s\n", e.what());
        }
        catch (const std::exception &e) {
            Base::Console().Error("%s\n", e.what());
        }
        catch (const char* e) {
            Base::Console().Error("%s\n", e);
        }
#ifndef FC_DEBUG
        catch (...) {
            Base::Console().Error("PropertySet::Save: Unknown C++ exception thrown. Try to continue...\n");
        }
#endif
        writer.decInd(); // indentation for the actual property
        writer.Stream() << writer.ind() << "</Property>" << endl;    
        writer.decInd(); // indentation for 'Property name'

    }
    writer.Stream() << writer.ind() << "</Properties>" << endl;
    writer.decInd(); // indentation for 'Properties Count'
}

void PropertySet::Restore(Base::XMLReader &reader)
{
    reader.readElement("Properties");
    int Cnt = reader.getAttributeAsInteger("Count");

    for (int i=0 ;i<Cnt ;i++) {
        reader.readElement("Property");
        const char* PropName = reader.getAttribute("name");
        const char* TypeName = reader.getAttribute("type");
        Property* prop = getPropertyByName(PropName);
        try {
            if (!prop) {
                const char *doc=0;
                if (reader.hasAttribute("doc"))
                    doc = reader.getAttribute("doc");
                prop = addProperty(TypeName, PropName, doc);
            }
        }
        catch(const Base::Exception& e) {
            // only handle this exception type
            Base::Console().Warning(e.what());
        }
        // NOTE: We must also check the type of the current property because a
        // subclass of PropertyContainer might change the type of a property but
        // not its name. In this case we would force to read-in a wrong property
        // type and the behaviour would be undefined.
        try {
            if (prop && strcmp(prop->getTypeId().getName(), TypeName) == 0)
                prop->Restore(reader);
        }
        catch (const Base::XMLParseException&) {
            throw; // re-throw
        }
        catch (const Base::Exception &e) {
            Base::Console().Error("%s\n", e.what());
        }
        catch (const std::exception &e) {
            Base::Console().Error("%s\n", e.what());
        }
        catch (const char* e) {
            Base::Console().Error("%s\n", e);
        }
#ifndef FC_DEBUG
        catch (...) {
            Base::Console().Error("PropertyContainer::Restore: Unknown C++ exception thrown");
        }
#endif
        reader.readEndElement("Property");
    }
    reader.readEndElement("Properties");
}
