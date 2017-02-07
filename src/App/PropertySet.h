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


#ifndef APP_PROPERTYSET_H
#define APP_PROPERTYSET_H

// Std. configurations


#include <vector>
#include <string>
#include "Property.h"

namespace Base {
class Writer;
}

namespace App
{
class DocumentObject;

/** Set Property
 *  Main Purpose of this property is to contain other, dynamic properties
 */
 
/// a structure to contain a property and its meta-data
struct AppExport PropertySetData
{
    const char* Docu;
    const char* Type;
    Property* Prop;
};

class AppExport PropertySet : public Property
{
    TYPESYSTEM_HEADER();

public:
    /// Constructor
    PropertySet();
    /// Destructor
    ~PropertySet();
    /// Sum of memory sizes of included properties
    unsigned int getMemSize (void) const;
    /// Size of the properties map
    int getSize(void) const;
    /// get a list of names
    std::vector<std::string> getPropertiesNames() const;
    /// find a property by its name
    Property *getProperty(const char* name) const;
    /// get the Type of a named Property
    const char* getPropertyType(const char *name) const;
    /// get the doc of a named Property
    const char* getPropertyDocumentation(const char *name) const;
    /// add a dynamic property.
    Property* addProperty(const char* type, const char* name=0, const char* doc=0);
    /// removes a property on the fly
    bool removeProperty(const char* name);
    /// index operator
    Property* operator[] (const char* name) const;

    /// Save/Restore
    void Save (Base::Writer &writer) const;
    void Restore(Base::XMLReader &reader);
    Property *Copy(void) const;
    void Paste(const Property &from);

private:
    /// Encodes an attribute upon saving.
    std::string encodeAttribute(const std::string&) const;
    std::string getUniquePropertyName(const char *Name) const;
    PropertySetData *getPropertyData(const char* name) const;
    /// The name/property map
    std::map<std::string,PropertySetData> _mValueMap;
};


} // namespace App


#endif // APP_PROPERTYSET_H
