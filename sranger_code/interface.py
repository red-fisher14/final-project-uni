import sys
import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from rclpy.qos import QoSPresetProfiles
from sensor_msgs.msg import LaserScan

SCAN_THRESHOLD = 0.5 # Metres per second

class Interface(Node):
    def __init__(self):
        super().__init__('interface')

        self.move_subscription = self.create_subscription(Twist, '/move', self.move_callback, 10)
        self.stop_subscription = self.create_subscription(Twist, '/stop', self.stop_callback, 10)
        self.scan_subscriber = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            QoSPresetProfiles.SENSOR_DATA.value)
        
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.obstacle_publisher = self.create_publisher(Empty, '/obstacle', 10)

    def move_callback(self, msg):
        self.cmd_vel_publisher.publish(msg)

    def stop_callback(self, msg):
        msg2 = Twist()
        self.cmd_vel_publisher.publish(msg2)

    def scan_callback(self, msg):
        # Group scan ranges into 4 segments
        # Front, left, and right segments are each 60 degrees
        # Back segment is 180 degrees
        front_ranges = msg.ranges[331:359] + msg.ranges[0:30] # 30 to 331 degrees (30 to -30 degrees)

        # Store True/False values for each sensor segment, based on whether the nearest detected obstacle is closer than SCAN_THRESHOLD
        if min(front_ranges) < SCAN_THRESHOLD:
            msg = Empty()
            self.obstacle_publisher.publish(msg)

    def destroy_node(self):
        msg = Twist()
        self.cmd_vel_publisher.publish(msg)
        super().destroy_node()

def main(args=None):
    rclpy.init(args = args, signal_handler_options = SignalHandlerOptions.NO)
    node = Interface()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    except ExternalShutdownException:
        sys.exit(1)
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()