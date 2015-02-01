
add_subdirectory(App)

if(BUILD_GUI)
    add_subdirectory(Gui)
endif(BUILD_GUI)

INSTALL(
    FILES
        Init.py
        InitGui.py
    DESTINATION
        Mod/Path
)

SET(PathScripts_SRCS
    PathScripts/__init__.py
    PathScripts/PostUtils.py
    PathScripts/example_pre.py
    PathScripts/opensbp_pre.py
    PathScripts/example_post.py
    PathScripts/linuxcnc_post.py
    PathScripts/comparams_post.py
    PathScripts/TooltableEditor.py
    PathScripts/PathProfile.py
    PathScripts/PathPocket.py
    PathScripts/PathDrilling.py
    PathScripts/PathDressup.py
    PathScripts/PathHop.py
    PathScripts/PathUtils.py
    PathScripts/PathSelection.py
    PathScripts/PathFixture.py
    PathScripts/PathCopy.py
    PathScripts/PathCompoundExtended.py
    PathScripts/PathProject.py
    PathScripts/PathToolTableEdit.py
    PathScripts/PathStock.py
    PathScripts/PathPlane.py
)

ADD_CUSTOM_TARGET(PathScripts ALL
    SOURCES ${PathScripts_SRCS}
)

fc_copy_sources(PathScripts "${CMAKE_BINARY_DIR}/Mod/Path" ${PathScripts_SRCS})

INSTALL(
    FILES
        ${PathScripts_SRCS}
    DESTINATION
        Mod/Path/PathScripts
       )

INSTALL(
    FILES
        DemoParts/hole_puzzle.fcstd
        DemoParts/motor_mount_inch.fcstd
        DemoParts/strange_part_with_holes.fcstd
    DESTINATION
        ${CMAKE_INSTALL_DATADIR}/Mod/Path/DemoParts
       )
