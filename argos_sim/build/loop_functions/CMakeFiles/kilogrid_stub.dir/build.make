# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.16

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/antoine/swarm_aggregation/argos_sim/ARGoS_simulation

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/antoine/swarm_aggregation/argos_sim/build

# Include any dependencies generated for this target.
include loop_functions/CMakeFiles/kilogrid_stub.dir/depend.make

# Include the progress variables for this target.
include loop_functions/CMakeFiles/kilogrid_stub.dir/progress.make

# Include the compile flags for this target's objects.
include loop_functions/CMakeFiles/kilogrid_stub.dir/flags.make

loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.o: loop_functions/CMakeFiles/kilogrid_stub.dir/flags.make
loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.o: loop_functions/kilogrid_stub_autogen/mocs_compilation.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/antoine/swarm_aggregation/argos_sim/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.o"
	cd /home/antoine/swarm_aggregation/argos_sim/build/loop_functions && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.o -c /home/antoine/swarm_aggregation/argos_sim/build/loop_functions/kilogrid_stub_autogen/mocs_compilation.cpp

loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.i"
	cd /home/antoine/swarm_aggregation/argos_sim/build/loop_functions && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/antoine/swarm_aggregation/argos_sim/build/loop_functions/kilogrid_stub_autogen/mocs_compilation.cpp > CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.i

loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.s"
	cd /home/antoine/swarm_aggregation/argos_sim/build/loop_functions && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/antoine/swarm_aggregation/argos_sim/build/loop_functions/kilogrid_stub_autogen/mocs_compilation.cpp -o CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.s

loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.o: loop_functions/CMakeFiles/kilogrid_stub.dir/flags.make
loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.o: /home/antoine/swarm_aggregation/argos_sim/ARGoS_simulation/loop_functions/kilogrid_stub.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/antoine/swarm_aggregation/argos_sim/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.o"
	cd /home/antoine/swarm_aggregation/argos_sim/build/loop_functions && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.o -c /home/antoine/swarm_aggregation/argos_sim/ARGoS_simulation/loop_functions/kilogrid_stub.cpp

loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.i"
	cd /home/antoine/swarm_aggregation/argos_sim/build/loop_functions && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/antoine/swarm_aggregation/argos_sim/ARGoS_simulation/loop_functions/kilogrid_stub.cpp > CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.i

loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.s"
	cd /home/antoine/swarm_aggregation/argos_sim/build/loop_functions && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/antoine/swarm_aggregation/argos_sim/ARGoS_simulation/loop_functions/kilogrid_stub.cpp -o CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.s

# Object files for target kilogrid_stub
kilogrid_stub_OBJECTS = \
"CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.o" \
"CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.o"

# External object files for target kilogrid_stub
kilogrid_stub_EXTERNAL_OBJECTS =

loop_functions/libkilogrid_stub.so: loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub_autogen/mocs_compilation.cpp.o
loop_functions/libkilogrid_stub.so: loop_functions/CMakeFiles/kilogrid_stub.dir/kilogrid_stub.cpp.o
loop_functions/libkilogrid_stub.so: loop_functions/CMakeFiles/kilogrid_stub.dir/build.make
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libdl.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libpthread.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libfreeimage.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libfreeimageplus.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libGL.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libGLU.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libglut.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libXmu.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libXi.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libQt5Widgets.so.5.12.8
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libQt5Gui.so.5.12.8
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/liblua5.3.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libm.so
loop_functions/libkilogrid_stub.so: /usr/lib/x86_64-linux-gnu/libQt5Core.so.5.12.8
loop_functions/libkilogrid_stub.so: loop_functions/CMakeFiles/kilogrid_stub.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/antoine/swarm_aggregation/argos_sim/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Linking CXX shared module libkilogrid_stub.so"
	cd /home/antoine/swarm_aggregation/argos_sim/build/loop_functions && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/kilogrid_stub.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
loop_functions/CMakeFiles/kilogrid_stub.dir/build: loop_functions/libkilogrid_stub.so

.PHONY : loop_functions/CMakeFiles/kilogrid_stub.dir/build

loop_functions/CMakeFiles/kilogrid_stub.dir/clean:
	cd /home/antoine/swarm_aggregation/argos_sim/build/loop_functions && $(CMAKE_COMMAND) -P CMakeFiles/kilogrid_stub.dir/cmake_clean.cmake
.PHONY : loop_functions/CMakeFiles/kilogrid_stub.dir/clean

loop_functions/CMakeFiles/kilogrid_stub.dir/depend:
	cd /home/antoine/swarm_aggregation/argos_sim/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/antoine/swarm_aggregation/argos_sim/ARGoS_simulation /home/antoine/swarm_aggregation/argos_sim/ARGoS_simulation/loop_functions /home/antoine/swarm_aggregation/argos_sim/build /home/antoine/swarm_aggregation/argos_sim/build/loop_functions /home/antoine/swarm_aggregation/argos_sim/build/loop_functions/CMakeFiles/kilogrid_stub.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : loop_functions/CMakeFiles/kilogrid_stub.dir/depend

