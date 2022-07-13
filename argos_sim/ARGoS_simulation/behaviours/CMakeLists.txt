if(ARGOS_BUILD_FOR_SIMULATOR)
  include_directories(${CMAKE_SOURCE_DIR}/argos3/plugins/robots/kilobot/control_interface)

add_executable(social_behavior agent.h social_behavior.c)
if(UNIX AND NOT APPLE)
  target_link_libraries(social_behavior  argos3plugin_simulator_kilolib rt m)
else(UNIX AND NOT APPLE)
  target_link_libraries(social_behavior  argos3plugin_simulator_kilolib)
endif()

endif(ARGOS_BUILD_FOR_SIMULATOR)
