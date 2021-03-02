cmake_minimum_required(VERSION 3.0.2)
project(nl_robot_console)

find_package(catkin REQUIRED COMPONENTS
      message_generation
      grammar_parser
      robocup_knowledge
)

catkin_python_setup()

# Generate services in the 'srv' folder
add_service_files(
    FILES
    TextCommand.srv
)

generate_messages(DEPENDENCIES)

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES bla
  CATKIN_DEPENDS message_runtime
#  DEPENDS system_lib
)
