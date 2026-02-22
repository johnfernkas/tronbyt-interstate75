# MicroPython native module cmake file for webpdec

add_library(usermod_webpdec INTERFACE)

target_sources(usermod_webpdec INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/webpdec.c
)

target_include_directories(usermod_webpdec INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
)

target_link_libraries(usermod INTERFACE usermod_webpdec)