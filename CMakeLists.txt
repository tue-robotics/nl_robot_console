cmake_minimum_required(VERSION 2.8.3)
project(nl_robot_console)

find_package(catkin REQUIRED COMPONENTS
      message_generation
      std_msgs
      grammar_parser
)

catkin_python_setup()

# Generate services in the 'srv' folder
add_service_files(
    FILES
    TextCommand.srv
)

generate_messages(DEPENDENCIES std_msgs)

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES bla
#  CATKIN_DEPENDS other_catkin_pkg
#  DEPENDS system_lib
)
