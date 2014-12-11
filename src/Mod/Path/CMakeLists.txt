
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

INSTALL(
    FILES
        PathScripts/__init__.py
        PathScripts/find_outer_profile.py
        PathScripts/heeks_funcs.py
        PathScripts/parseGroups.py
        PathScripts/toolpathparams.py
        PathScripts/pre_example.py
        PathScripts/post_example.py
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
