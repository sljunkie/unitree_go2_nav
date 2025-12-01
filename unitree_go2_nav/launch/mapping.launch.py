from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, SetLaunchConfiguration
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            name = 'use_sim_time',
            default_value = 'false', choices = ['true', 'false'],
            description = 'Use simulation (Gazebo) clock'
        ),
        DeclareLaunchArgument(
            name = 'deskewing',
            default_value = 'false', choices = ['true', 'false'],
            description = 'Enable lidar deskewing'
        ),
        DeclareLaunchArgument(
            name = 'use_rtabmapviz',
            default_value = 'true', choices = ['true', 'false'],
            description='Start rtabmapviz node'
        ),
        DeclareLaunchArgument(
            name = 'use_map_rviz',
            default_value = 'true', choices = ['true', 'false'],
            description='Open Rviz for visualization'
        ),
        SetLaunchConfiguration(
            name = 'config_file',
            value = 'mapping.rviz'
        ),
        SetLaunchConfiguration(
            name = 'rvizconfig',
            value = PathJoinSubstitution([
                FindPackageShare('unitree_go2_nav'),
                'config',
                LaunchConfiguration('config_file')
            ])
        ),
        Node(
            package = 'rtabmap_slam', executable = 'rtabmap', output = 'screen',
            parameters = [{
                'frame_id'              : 'utlidar_lidar',
                'subscribe_depth'       : False,
                'subscribe_rgb'         :False,
                'subscribe_scan_cloud'  : True,
                'approx_sync'           : True
                'wait_for_transform'    : 0.3,
                'use_sim_time'          : LaunchConfiguration('use_sim_time'),
                # added to resolve frequency mismatch between scan cloud and odom
                'sync_queue_size'       : 50,
                'topic_queue_size'      : 50,
            }],
            remappings = [
                ('scan_cloud', '/utlidar/cloud_deskewed'),
                ('odom', '/utlidar/robot_odom')
            ]
        ), 
        Node(
            package = 'unitree_go2_nav', executable = 'odomTfPublisher', output = 'screen',
            remappings=[
                ('odom', '/utlidar/robot_odom')
            ]
        ),
        Node(
            package = 'rviz2', executable = 'rviz2',
            arguments = [
                    '-d', LaunchConfiguration('rvizconfig')
            ],
            condition = IfCondition(LaunchConfiguration('use_map_rviz'))
        )
    ])
