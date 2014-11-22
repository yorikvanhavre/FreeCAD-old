if(MSVC)
    add_definitions(-DHAVE_ACOSH -DHAVE_ASINH -DHAVE_ATANH -DEIGEN2_SUPPORT)
else(MSVC)
    add_definitions(-DHAVE_LIMITS_H -DHAVE_CONFIG_H -DEIGEN2_SUPPORT)
endif(MSVC)


include_directories(
    ${CMAKE_BINARY_DIR}
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_BINARY_DIR}/src
    ${CMAKE_CURRENT_BINARY_DIR}
    ${Boost_INCLUDE_DIRS}
    ${OCC_INCLUDE_DIR}
    ${EIGEN3_INCLUDE_DIR}
    ${PYTHON_INCLUDE_PATH}
    ${ZLIB_INCLUDE_DIR}
    ${QT_INCLUDE_DIR}
    ${XERCESC_INCLUDE_DIR}
)
link_directories(${OCC_LIBRARY_DIR})

if(MSVC)
    set(Part
        ${QT_QTCORE_LIBRARY}
        ${QT_QTCORE_LIBRARY_DEBUG}
        FreeCADApp
    )
else(MSVC)
    set(Part
        ${QT_QTCORE_LIBRARY}
        FreeCADApp
    )
endif(MSVC)

generate_from_xml(CommandPy)
generate_from_xml(PathPy)

SET(Python_SRCS
    CommandPy.xml
    CommandPyImp.cpp
    PathPy.xml
    PathPyImp.cpp
)

SET(Mod_SRCS
    AppPath.cpp
    AppPathPy.cpp
    PreCompiled.cpp
    PreCompiled.h
)

SET(Path_SRCS
    Command.cpp
    Command.h
    Path.cpp
    Path.h
    PropertyPath.cpp
    PropertyPath.h
    FeaturePath.cpp
    FeaturePath.h
    ${Mod_SRCS}
    ${Python_SRCS}
)

SOURCE_GROUP("Python" FILES ${Python_SRCS})
SOURCE_GROUP("Module" FILES ${Mod_SRCS})

SET(Path_Scripts
    Init.py
)

add_library(Path SHARED ${Path_SRCS})
target_link_libraries(Path ${Path_LIBS})

fc_target_copy_resource(Path 
    ${CMAKE_SOURCE_DIR}/src/Mod/Path
    ${CMAKE_BINARY_DIR}/Mod/Path
    ${Path_Scripts})

fc_target_copy_resource(Path 
    ${CMAKE_SOURCE_DIR}/src/Mod/Path
    ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_DATADIR}/Mod/Path
    ${Path_Resources})

SET_BIN_DIR(Path Path /Mod/Path)
SET_PYTHON_PREFIX_SUFFIX(Path)

INSTALL(TARGETS Path DESTINATION ${CMAKE_INSTALL_LIBDIR})
