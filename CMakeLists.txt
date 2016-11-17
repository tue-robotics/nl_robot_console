cmake_minimum_required(VERSION 2.8.3)
project(nl_robot_console)

catkin_python_setup()

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES bla
#  CATKIN_DEPENDS other_catkin_pkg
#  DEPENDS system_lib
)

find_package(catkin REQUIRED COMPONENTS
      message_generation
)

# Generate services in the 'srv' folder
add_service_files(
    FILES
    TextCommand.srv
)

