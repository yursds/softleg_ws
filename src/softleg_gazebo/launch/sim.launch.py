import os
import launch_ros.descriptions

from launch                             import LaunchDescription
from launch.actions                     import IncludeLaunchDescription, RegisterEventHandler
from launch.substitutions               import PathJoinSubstitution
from launch.launch_description_sources  import PythonLaunchDescriptionSource
from launch_ros.substitutions           import FindPackageShare
from launch_ros.actions                 import Node
from launch.event_handlers              import OnProcessExit

from ament_index_python.packages        import get_package_share_directory


URDF_FILE = 'softlegisaac.urdf'

def generate_launch_description():
    
    softleg_description_path    = os.path.join(get_package_share_directory('softleg_description'), 'urdf', URDF_FILE)
    softleg_description_content = open(softleg_description_path).read()
    
    #print(f"urdf_file_path : {softleg_description_path}")
    #print(f"urdf_file_content : {softleg_description_content}")
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"])]
        ),
        launch_arguments = {"pause": "true", "verbose": "false"}.items(),
    )


    node_robot_state_publisher = Node(
        package    = "robot_state_publisher",
        executable = "robot_state_publisher",
        name       = "robot_state_publisher",
        parameters = [{"robot_description":softleg_description_content}],
        arguments  = [softleg_description_path],
        output     = {
            "stdout": "screen",
            "stderr": "screen",
        },
    )

    spawn_entity = Node(
        package    = "gazebo_ros",
        executable = "spawn_entity.py",
        arguments  = [
            "-topic", "robot_description", "-entity", "softleg",
            "-x", "0.0", "-y", "0.0", "-z", "0.0",
        ],
        output     = {
            "stdout": "screen",
            "stderr": "screen",
        },
    )

    joint_state_broadcaster_spawner = Node(
        package    = "controller_manager",
        executable = "spawner",
        arguments  = ["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output     = {
            "stdout": "screen",
            "stderr": "screen",
        },
    )

    PD_jnt_control = Node(
        package    = "controller_manager",
        executable = "spawner",
        arguments  = ["PD_control", "--controller-manager", "/controller_manager"],
        output     = {
            "stdout": "screen",
            "stderr": "screen",
        },
    )

    launcher = LaunchDescription([
        launch_ros.actions.SetParameter(name='use_sim_time', value=True),
        gazebo,
        node_robot_state_publisher,
        spawn_entity,
        RegisterEventHandler(
            event_handler = OnProcessExit(
                target_action = spawn_entity,
                on_exit       = [joint_state_broadcaster_spawner],
            )
        ),
        RegisterEventHandler(
            event_handler = OnProcessExit(
                target_action = spawn_entity,
                on_exit       = [PD_jnt_control],
            )
        ),
    ])
    
    return launcher